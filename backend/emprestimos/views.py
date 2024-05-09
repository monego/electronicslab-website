# views.py

from .models import Equipamento
from .serializers import EquipamentoSerializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated


class EquipamentoViewSet(ModelViewSet):
    queryset = Equipamento.objects.all()
    authentication_classes = (BasicAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = EquipamentoSerializer