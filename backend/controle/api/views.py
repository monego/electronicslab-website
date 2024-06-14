from controle.api.serializers import (
    AtividadesSerializer,
    ControleAcessoSerializer,
    EmprestimoSerializer,
    EquipamentoSerializer,
    ManutencaoSerializer,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from controle.models import (
    Atividades,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    Manutencao,
)


class AtividadesViewSet(ModelViewSet):
    queryset = Atividades.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AtividadesSerializer

class ControleAcessoViewSet(ModelViewSet):
    queryset = ControleAcesso.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ControleAcessoSerializer
    def hora_saida_is_null(self):
        queryset = ControleAcesso.objects.filter(hora_saida_isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class EmprestimoViewSet(ModelViewSet):
    queryset = Emprestimo.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = EmprestimoSerializer

class EquipamentoViewSet(ModelViewSet):
    queryset = Equipamento.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = EquipamentoSerializer

class ManutencaoViewSet(ModelViewSet):
    queryset = Manutencao.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ManutencaoSerializer

