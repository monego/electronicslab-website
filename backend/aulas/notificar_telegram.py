from datetime import timedelta, datetime
from django.conf import settings
from django.utils.timezone import now, localtime
from aulas.models import Aula
from collections import defaultdict
import httpx
import logging

logger = logging.getLogger(__name__)

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

    message_parts = []
    message_parts.append(f"NUPEDEE \\- Aulas Agendadas para {tomorrow.strftime('%d/%m/%Y')}:\n")

    aulas_by_andar = defaultdict(list)
    for aula in aulas:
        andar = aula.sala.andar
        aulas_by_andar[andar].append(aula)

    for andar in sorted(aulas_by_andar.keys()):
        message_parts.append(f"*{andar}° Andar*\n")
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

            message_parts.append(
                f"   {warning_emoji}\[{aula.inicio.strftime('%H:%M')}\-{aula.fim.strftime('%H:%M')}\]"
                f"\[{aula.sala.codigo}\] {professor_name} \\- {disciplina_name}\n"
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


