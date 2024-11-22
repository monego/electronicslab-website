from .serializers import AulaSerializer
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Q
from django.conf import settings
from django.utils.timezone import make_aware, now, localtime, timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from zoneinfo import ZoneInfo
from aulas.models import Aula
from root.models import Sala
import httpx
import json


class IsCeleryWorker(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        if request.method == 'POST':
            return (
                request.headers.get("Authorization")
                == f"Bearer {settings.CELERY_TOKEN}"
            )

        return False


class AulasViewSet(ModelViewSet):
    queryset = Aula.objects.all()
    serializer_class = AulaSerializer
    permission_classes = [IsCeleryWorker]

    def create(self, request, *args, **kwargs):
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
                titulo_split = titulo.split(' - ')
                disciplina = titulo_split[0]
                professor = titulo_split[-1]

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

        return Response(
            {"detail": "OK"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='calendario')
    def get_for_calendar(self, request, *args, **kwargs):
        codigo = int(request.query_params.get('codigo'))
        inicio = request.query_params.get('inicio')
        fim = request.query_params.get('fim')

        sala = Sala.objects.filter(codigo=codigo).first()

        aulas = Aula.objects.filter(
            sala=sala,
            inicio__date__gte=inicio,
            inicio__date__lte=fim,
        )

        serializer = self.get_serializer(aulas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='hoje')
    def get_for_today(self, request, *args, **kwargs):
        fim = localtime(now())

        aulas = Aula.objects.filter(
            fim__gt=fim,
            fim__date=fim.date(),
        )

        serializer = self.get_serializer(aulas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
