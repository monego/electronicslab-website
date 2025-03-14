from .serializers import AulaSerializer
from django.utils.timezone import now, localtime
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
