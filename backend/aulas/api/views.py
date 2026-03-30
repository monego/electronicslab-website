from .serializers import AulaSerializer
from django.utils.timezone import now, localtime
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from aulas.models import Aula
from root.models import Sala


class AulasViewSet(ModelViewSet):
    queryset = Aula.objects.all()
    serializer_class = AulaSerializer
    permission_classes = []

    @action(detail=False, methods=['get'], url_path='update')
    def get_for_update(self, request, *args, **kwarts):
        self.create(request)
        return Response(
            {"detail": "OK"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='calendario')
    def get_for_calendar(self, request, *args, **kwargs):
        codigo = request.query_params.get('codigo')
        inicio = request.query_params.get('inicio')
        fim = request.query_params.get('fim')

        if not all([codigo, inicio, fim]):
            return Response(
                {"detail": "Parâmetros 'codigo', 'inicio' e 'fim' são obrigatórios."},
                status=status.HTTP_400_BAD_REQUEST
            )

        sala = Sala.objects.filter(codigo=codigo).first()
        if not sala:
            return Response(
                {"detail": "Sala não encontrada."},
                status=status.HTTP_404_NOT_FOUND
            )

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
            fim__date=fim.date(),
        )

        serializer = self.get_serializer(aulas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='amanha')
    def get_for_tomorrow(self, request, *args, **kwargs):
        tomorrow = localtime(now()).date() + timedelta(days=1)

        aulas = Aula.objects.filter(
            fim__date=tomorrow,
        )

        serializer = self.get_serializer(aulas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    @action(detail=False, methods=['get'], url_path='data')
    def get_for_date(self, request, *args, **kwargs):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {"detail": "Parâmetro 'date' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )

        aulas = Aula.objects.filter(
            inicio__date=date_str,
        )

        serializer = self.get_serializer(aulas, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
