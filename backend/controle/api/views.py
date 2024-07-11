from controle.api.serializers import (
    AtividadesSerializer,
    AusenciaSerializer,
    ControleAcessoSerializer,
    EmprestimoSerializer,
    EquipamentoSerializer,
    HorarioTrabalhoSerializer,
    ManutencaoSerializer,
)

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from controle.models import (
    Atividades,
    Ausencia,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    HorarioTrabalho,
    Manutencao,
)


class AtividadesViewSet(ModelViewSet):
    queryset = Atividades.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AtividadesSerializer


class AusenciaViewSet(ModelViewSet):
    queryset = Ausencia.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AusenciaSerializer


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


class HorarioTrabalhoViewSet(ModelViewSet):
    queryset = HorarioTrabalho.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HorarioTrabalhoSerializer


class ManutencaoViewSet(ModelViewSet):
    queryset = Manutencao.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ManutencaoSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        # Filter users based on permissions
        if request.user.has_perm("auth.view_user"):
            users = User.objects.all().values("id", "username")
            return Response(list(users))
        else:
            return Response(
                {"error": "Sem permissão para acessar a lista de usuários."}, status=403
            )

    def retrieve(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            return Response({"username": user.username})
        except User.DoesNotExist:
            return Response({"error": "Usuário não encontrado"}, status=404)

