from controle.api.serializers import (
    AtividadesSerializer,
    AusenciaSerializer,
    ControleAcessoSerializer,
    EmprestimoSerializer,
    EquipamentoSerializer,
    HorarioTrabalhoSerializer,
    ManutencaoSerializer,
)

from controle.models import Pessoa
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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

    def list(self, request, *args, **kwargs):
        user = request.user

        if user.username == 'paulo':
            queryset = self.get_queryset()
        else:
            queryset = self.get_queryset().filter(funcionarios=user)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        descricao = request.data['descricao']
        observacao = request.data['observacao']
        username = request.user

        Atividades.objects.create(
            funcionario=User.objects.get(username=username),
            descricao=descricao,
            observacao=observacao,
            hora_concluida=None,
        )


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

class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = EmprestimoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        primary_key = instance.pk
        return Response({'id': primary_key})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter based on a query parameter: ?all=true
        all = request.query_params.get('all', None)

        if not all:
            queryset = queryset.exclude(devolucao__isnull=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        identificador = request.data.get('identificador')
        matricula = request.data.get('matricula')
        obs = request.data.get('obs')
        items = request.data.get('items')

        try:
            responsavel = Pessoa.objects.get(matricula=matricula)
        except Pessoa.DoesNotExist:
            return Response({'detail': 'Não há uma pessoa com essa matrícula'})

        print(responsavel.id)

        data = {
            'identificador': identificador,
            'responsavel': responsavel.id,
            'funcionario': request.user.id,
            'local': obs,
            'items': items,
            'devolucao': None
        }

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(
            responsavel=Pessoa.objects.get(matricula=self.request.data['matricula']),
            funcionario=self.request.user
        )

    @action(detail=False, methods=['patch'], url_path='byidentifier')
    def patch_by_identifier(self, request, *args, **kwargs):
        identificador = request.data.get('identificador', None)
        if not identificador:
            return Response({'detail': 'Identificador de empréstimo é necessário.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            obj = Emprestimo.objects.get(identificador=identificador)
        except Emprestimo.DoesNotExist:
            return Response({'detail': 'Não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        obj.devolucao = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

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

