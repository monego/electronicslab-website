from collections import defaultdict
from datetime import datetime, timedelta
from django.conf import settings
from django.db import IntegrityError
from django.db.models import Q
from django.utils.timezone import localtime, make_aware, now
from aulas.models import Aula
from aulas.api.serializers import AulaSerializer
from root.models import Sala
from zoneinfo import ZoneInfo
import json
import httpx
import logging

logger = logging.getLogger(__name__)

def update_aulas_task():

    def title_split(titulo):
        if '/' in titulo:
            return titulo.split('/')
        return titulo.split('-')

    url = settings.URL_CPD
    salas = Sala.objects.values_list('codigo', flat=True)
    data_atual = now()
    inicio_total = data_atual.strftime('%d/%m/%Y')
    fim_total = data_atual.strftime('31/12/%Y')

    for sala in salas:

        chaves_api = []
        aulas_modificadas = []

        data = {
            "espaco": sala,
            "inicio": inicio_total,
            "fim": fim_total,
            "apenasDeferidos": True,
        }

        response = json.loads(httpx.post(url, json=data).text)

        sala_object = Sala.objects.filter(codigo=sala).first()

        aulas_existentes = Aula.objects.filter(sala=sala_object).values(
            "inicio", "fim", "sala"
        )

        aulas_existentes_set = set(
            (aula["inicio"], aula["fim"], aula["sala"]) for aula in aulas_existentes
        )

        for aula in response:
            inicio = datetime.strptime(aula['start'], "%Y-%m-%d %H:%M:%S")
            fim = datetime.strptime(aula['end'], "%Y-%m-%d %H:%M:%S")

            inicio = make_aware(inicio)
            fim = make_aware(fim)

            chave_aula = (inicio, fim, sala_object.id)

            chaves_api.append(chave_aula)

            titulo = aula['title']
            titulo_split = title_split(titulo)
            disciplina = titulo_split[1]
            professor = titulo_split[0]

            if chave_aula not in aulas_existentes_set:

                nova_aula = {
                    'inicio': inicio,
                    'fim': fim,
                    'sala': sala_object.pk,
                    'professor': professor,
                    'disciplina': disciplina
                }

                serializer = AulaSerializer(data=nova_aula)

                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except IntegrityError:
                    pass
            else:
                aula_existente = Aula.objects.get(
                    inicio=inicio, fim=fim, sala=sala_object
                )
                aula_existente.professor = professor
                aula_existente.disciplina = disciplina
                aulas_modificadas.append(aula_existente)

        sao_paulo_timezone = ZoneInfo("America/Sao_Paulo")

        aulas_existentes_set_sp = [
            (
                item[0].astimezone(sao_paulo_timezone),
                item[1].astimezone(sao_paulo_timezone),
                item[2],
            )
            for item in aulas_existentes_set
        ]

        chaves_excluir = set(aulas_existentes_set_sp) - set(chaves_api)

        if chaves_excluir:
            Aula.objects.filter(
                Q(inicio__in=[k[0] for k in chaves_excluir]) &
                Q(fim__in=[k[1] for k in chaves_excluir]) &
                Q(sala__in=[k[2] for k in chaves_excluir])
            ).delete()


def escape_markdown_v2(text):
    """
    Escapes reserved characters for Telegram's MarkdownV2 parse mode.
    """
    if not text:
        return ""
    # Reserved characters in MarkdownV2: _ * [ ] ( ) ~ ` > # + - = | { } . !
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return "".join(f"\\{c}" if c in escape_chars else c for c in text)


def notify_aulas_task():
    telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
    telegram_channel_id = settings.AULAS_TELEGRAM_CHANNEL

    if not telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN is not set in Django settings.")
        return
    if not telegram_channel_id:
        logger.error("AULAS_TELEGRAM_CHANNEL is not set in Django settings.")
        return

    tomorrow = localtime(now()).date() + timedelta(days=1)

    aulas = Aula.objects.filter(inicio__date=tomorrow).order_by(
        'sala__andar', 'inicio', 'sala__codigo'
    ).select_related('sala')

    if not aulas:
        logger.info(f"No aulas found for tomorrow ({tomorrow.strftime('%d/%m/%Y')}). Not sending Telegram notification.")
        return

    message_parts: list[str] = []
    message_parts.append(f"NUPEDEE \\- Aulas Agendadas para {tomorrow.strftime('%d/%m/%Y')}:\n")

    aulas_by_andar = defaultdict(list)
    for aula in aulas:
        andar = aula.sala.andar
        aulas_by_andar[andar].append(aula)

    for andar in sorted(aulas_by_andar.keys()):
        message_parts.append(f"*{escape_markdown_v2(str(andar))}° Andar*\n")
        for aula in aulas_by_andar[andar]:
            # Professor name: first and last name
            professor_name_parts = aula.professor.split(' ')
            if len(professor_name_parts) >= 2:
                professor_name = f"{professor_name_parts[0]} {professor_name_parts[-1]}"
            else:
                professor_name = aula.professor # Fallback if only one name

            # Disciplina: limit to 15 characters
            disciplina_name = aula.disciplina
            if len(disciplina_name) > 15:
                disciplina_name = disciplina_name[:15] + '...'

            # Early/late class warning
            warning_emoji = ""
            start_time = aula.inicio.time()
            end_time = aula.fim.time()
            if start_time < datetime.strptime("08:30", "%H:%M").time() or \
               end_time > datetime.strptime("17:30", "%H:%M").time():
                warning_emoji = "⚠️ " # Emoji itself doesn't need escaping for MarkdownV2

            # Escape dynamic content
            professor_name = escape_markdown_v2(professor_name)
            disciplina_name = escape_markdown_v2(disciplina_name)
            sala_codigo = escape_markdown_v2(aula.sala.codigo)

            message_parts.append(
                f"   {warning_emoji}\\[{aula.inicio.strftime('%H:%M')}\\-{aula.fim.strftime('%H:%M')}\\]"
                f"\\[{sala_codigo}\\] {professor_name} \\- {disciplina_name}\n"
            )
        message_parts.append("\n") # Add a new line after each andar

    message_text = "".join(message_parts)
    # Telegram requires escaping certain characters for MarkdownV2
    # The following characters must be escaped: _, *, [, ], (, ), ~, `, >, #, +, -, =, |, {, }, ., !
    # Emojis don't need escaping.

    telegram_api_url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": telegram_channel_id,
        "text": message_text,
        "parse_mode": "MarkdownV2"
    }

    try:
        response = httpx.post(telegram_api_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Telegram notification sent successfully. Status code: {response.status_code}")
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting Telegram API: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Telegram API responded with an error status {e.response.status_code}: {e.response.text}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
