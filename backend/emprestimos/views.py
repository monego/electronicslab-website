# views.py

from .models import Equipamento
from .serializers import EquipamentoSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action


class EquipamentoViewSet(ModelViewSet):
    queryset = Equipamento.objects.all()
    serializer_class = EquipamentoSerializer

    @action(detail=True, methods=['post'])
    def update_db(self, request, pk=None):
        instancia = self.get_object()
        serializer = self.get_serializer(instancia, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'mensagem': 'Data updated!'})
