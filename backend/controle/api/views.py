from controle.api.serializers import (
    AtividadesSerializer,
    AtualizacaoAtividadeSerializer,
    AusenciaSerializer,
    ControleAcessoSerializer,
    EmprestimoSerializer,
    EquipamentoSerializer,
    HorarioTrabalhoSerializer,
    ManutencaoSerializer,
)

from django.contrib.auth.models import User
from django.db.models import Count
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
    AtualizacaoAtividade,
    Ausencia,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    HorarioTrabalho,
    Manutencao,
)
from root.models import Pessoa, Sala

class AtividadesViewSet(ModelViewSet):
    queryset = Atividades.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AtividadesSerializer

    def create(self, request, *args, **kwargs):

        funcionarios_username = request.data['funcionarios']
        funcionarios_id = []
        descricao = request.data['descricao']
        observacao = request.data['observacao']

        try:
            for funcionario_username in funcionarios_username:
                funcionarios_id.append(User.objects.get(username=funcionario_username))
        except User.DoesNotExist:
            return Response({'detail': 'Não há um usuário com esse nome'})

        data = {
            'funcionarios': funcionarios_id,
            'descricao': descricao,
            'observacao': observacao,
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

class AtualizacaoAtividadeViewSet(ModelViewSet):
    queryset = AtualizacaoAtividade.objects.all()
    serializer_class = AtualizacaoAtividadeSerializer

    def perform_create(self, serializer):
        atualizacao_atividade = serializer.save()
        if atualizacao_atividade.state:
            atualizacao_atividade

class AusenciaViewSet(ModelViewSet):
    queryset = Ausencia.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AusenciaSerializer


class ControleAcessoViewSet(ModelViewSet):
    queryset = ControleAcesso.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ControleAcessoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        primary_key = instance.pk
        return Response({'id': primary_key})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Filter based on a query parameter: ?all=true
        all = request.query_params.get('all', None)

        if not all:
            queryset = queryset.exclude(hora_saida__isnull=False)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        matricula = request.data.get('matricula')
        sala = request.data.get('sala')

        try:
            aluno = Pessoa.objects.get(matricula=matricula)
        except Pessoa.DoesNotExist:
            return Response({'detail': 'Não há uma pessoa com essa matrícula'})

        try:
            sala = Sala.objects.get(numero=sala)
        except Sala.DoesNotExist:
            return Response({'detail': 'Não há uma sala correspondente'})

        aluno_registrado = ControleAcesso.objects.filter(
            pessoa=aluno, hora_saida__isnull=True
        ).exists()

        if aluno_registrado:
            return Response(
                {
                    'detail': 'O aluno não pode estar em duas salas ao mesmo tempo!'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'pessoa': aluno.id,
            'sala': sala.id,
            'hora_saida': None
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
        serializer.save()

    @action(detail=False, methods=['patch'], url_path='bymatricula')
    def patch_by_matricula(self, request, *args, **kwargs):
        matricula = request.data.get('matricula', None)
        if not matricula:
            return Response({'detail': 'Matrícula do aluno é necessária.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            pessoa = Pessoa.objects.get(matricula=matricula)
        except Pessoa.DoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            obj = ControleAcesso.objects.get(pessoa=pessoa, hora_saida__isnull=True)
        except ControleAcesso.DoesNotExist:
            return Response({'detail': 'Acesso não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        obj.hora_saida = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

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
    permission_classes = (IsAuthenticated,)
    serializer_class = EquipamentoSerializer

    def get_queryset(self):
        return Equipamento.objects.annotate(num_manutencao=Count('manutencao'))

    @action(detail=True, methods=['post'])
    def upload_foto(self, request, pk=None):
        equipamento = self.get_object()
        serializer = EquipamentoSerializer(equipamento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def upload_manual(self, request, pk=None):
        equipamento = self.get_object()
        serializer = EquipamentoSerializer(equipamento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HorarioTrabalhoViewSet(ModelViewSet):
    queryset = HorarioTrabalho.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HorarioTrabalhoSerializer


class ManutencaoViewSet(ModelViewSet):
    queryset = Manutencao.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ManutencaoSerializer

    def list(self, request):
        queryset = self.get_queryset()

        # Filter based on a query parameter: ?all=true
        nome = request.query_params.get('nome', None)

        try:
            equipamento = Equipamento.objects.get(nome=nome)
        except Equipamento.DoesNotExist:
            return Response({'detail': 'Não há um equipamento com esse nome'})

        if nome:
            queryset = queryset.filter(equipamento=equipamento).reverse()

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        descricao = request.data.get('descricao')
        equipamento_nome = request.data.get('equipamento_nome')

        try:
            equipamento = Equipamento.objects.get(nome=equipamento_nome)
        except Equipamento.DoesNotExist:
            return Response({'detail': 'Não há um equipamento com esse nome'})

        data = {
            'descricao': descricao,
            'funcionario': request.user.id,
            'equipamento': equipamento.id
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
            funcionario=self.request.user
        )

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
