from controle.api.serializers import (
    AusenciaSerializer,
    ComprasSerializer,
    ControleAcessoSerializer,
    EmprestimoSerializer,
    EquipamentoSerializer,
    EquipamentoPublicoSerializer,
    HorarioTrabalhoSerializer,
    ItemEmprestimoSerializer,
    ManutencaoSerializer,
    OrcamentoSerializer,
)

from django.contrib.auth.models import User
from django.db.models import Count
from django.http import FileResponse
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from controle.models import (
    Ausencia,
    Compras,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    ItemEmprestimo,
    HorarioTrabalho,
    Manutencao,
    Orcamento,
)
from root.models import Pessoa, Sala

from barcode import Code39
from barcode.writer import ImageWriter
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

class AusenciaViewSet(ModelViewSet):
    queryset = Ausencia.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = AusenciaSerializer

    def create(self, request):
        data = {
            'inicio': request.data.get('inicio'),
            'fim': request.data.get('fim'),
            'motivo': request.data.get('motivo'),
            'funcionario': request.user.pk,
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

class ComprasViewSet(ModelViewSet):
    queryset = Compras.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ComprasSerializer

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

    def get_queryset(self):
        queryset = Emprestimo.objects.all()
        identificador = self.request.query_params.get('identificador', None)
        if identificador is not None:
            queryset = queryset.filter(identificador=identificador)
        return queryset

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
        items = request.data.get('items')
        obs = request.data.get('obs')

        try:
            responsavel = Pessoa.objects.get(matricula=matricula)
        except Pessoa.DoesNotExist:
            return Response({'detail': 'Não há uma pessoa com essa matrícula'})

        data = {
            'identificador': identificador,
            'responsavel': responsavel.id,
            'funcionario': request.user.id,
            'local': obs,
            'devolucao': None,
        }

        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
            emprestimo = serializer.save(
                responsavel=Pessoa.objects.get(
                    matricula=self.request.data["matricula"]
                ),
                funcionario=self.request.user,
            )

            for item in items:
                try:
                    equipamento = Equipamento.objects.get(patrimonio=item)
                    data = {
                        'emprestimo': emprestimo.pk,
                        'equipamento': equipamento.pk,
                    }
                    item_serializer = ItemEmprestimoSerializer(data=data)
                    item_serializer.is_valid(raise_exception=True)
                    item_serializer.save()
                except Equipamento.DoesNotExist:
                    data = {
                        'emprestimo': emprestimo.pk,
                        'nome': item,
                    }
                    item_serializer = ItemEmprestimoSerializer(data=data)
                    item_serializer.is_valid(raise_exception=True)
                    item_serializer.save()

            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except ValidationError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

        obj.encerrado = True
        obj.devolucao = timezone.now()
        obj.save()

        serializer = self.get_serializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='printsheet')
    def print_sheet(self, request, *args, **kwargs):
        start = int(request.query_params.get('inicio'))
        pages = int(request.query_params.get('paginas'))

        fig_w, fig_h = 113, 62
        text_size = 12

        buffer = BytesIO()

        c = canvas.Canvas(buffer, pagesize=A4)

        margin = 28

        width, height = A4

        num_columns = 3
        num_rows = 9

        code_list = range(start, start + num_columns*num_rows*pages)

        code_iter = iter(code_list)

        for page in range(1, pages + 1):

            cell_width = (width - 2 * margin) / num_columns
            cell_height = (height - 2 * margin) / num_rows

            for i in range(num_columns + 1):
                x = margin + i * cell_width
                c.line(x, margin, x, height - margin)

            for j in range(num_rows + 1):
                y = margin + j * cell_height
                c.line(margin, y, width - margin, y)

            for row in range(num_rows):
                for col in range(num_columns):

                    img = BytesIO()

                    Code39(
                        str(next(code_iter)),
                        writer=ImageWriter(),
                        add_checksum=False,
                    ).write(img)

                    code = ImageReader(img)

                    x = margin + col * cell_width
                    y = margin + (num_rows - row - 1) * cell_height

                    cell_center_x = x + cell_width / 2
                    cell_center_y = y + cell_height / 2

                    center_x = cell_center_x - fig_w / 2
                    center_y = cell_center_y - fig_h / 2

                    text_pipe = '|'
                    text_sign = '__________'
                    text_retdev = 'Retirada / Devolução'
                    text_under = "NUPEDEE - Autenticação de Registros de Empréstimo"
                    text_pages = f"{page}/{pages}"
                    text_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

                    text_pipe_w = c.stringWidth(text_pipe, "Helvetica", text_size)
                    text_sign_w = c.stringWidth(text_sign, "Helvetica", text_size)
                    text_retdev_w = c.stringWidth(text_retdev, "Helvetica", text_size)
                    text_h = text_size

                    centered_pipe_x = cell_center_x - text_pipe_w / 2
                    centered_sign_x = cell_center_x - text_sign_w / 2
                    centered_retdev_x = cell_center_x - text_retdev_w / 2

                    centered_y = cell_center_y - text_h / 2

                    c.drawImage(
                        code,
                        center_x,
                        center_y + 10,
                        width=fig_w,
                        height=fig_h,
                    )
                    c.drawString(centered_sign_x - 35, centered_y - 20, text_sign)
                    c.drawString(centered_pipe_x, centered_y - 25, text_pipe)
                    c.drawString(centered_sign_x + 35, centered_y - 20, text_sign)
                    c.drawString(centered_retdev_x + 5, centered_y - 35, text_retdev)
                    c.drawString(50, 820, text_date)
                    c.drawString(50, 10, text_under)
                    c.drawString(500, 10, text_pages)

            c.showPage()

        c.save()

        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename=f"folha_{start}.pdf",
        )

class EquipamentoViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EquipamentoSerializer

    def get_queryset(self):
        return Equipamento.objects.annotate(
            num_manutencao=Count('manutencao', distinct=True),
            num_emprestimo=Count('item_emprestimo', distinct=True)
        )

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

class EquipamentoPublicoViewSet(ModelViewSet):
    queryset = Equipamento.objects.all()
    permission_classes = []
    serializer_class = EquipamentoPublicoSerializer

class HorarioTrabalhoViewSet(ModelViewSet):
    queryset = HorarioTrabalho.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = HorarioTrabalhoSerializer

    def list(self, request):
        queryset = self.get_queryset()

        user_pk = request.user.pk

        queryset = queryset.filter(funcionario=user_pk)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'], url_path='byday')
    def patch_by_day(self, request, *args, **kwargs):
        dia = request.data.get('dia')
        inicio = request.data.get('inicio')
        inicio_intervalo = request.data.get('inicio_intervalo')
        fim_intervalo = request.data.get('fim_intervalo')
        fim = request.data.get('fim')
        user_pk = request.user.pk

        try:
            horario = HorarioTrabalho.objects.get(
                dia_da_semana=dia, funcionario=user_pk
            )
        except HorarioTrabalho.DoesNotExist:
            return Response({'detail': 'Não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        horario.inicio = inicio
        horario.inicio_intervalo = inicio_intervalo
        horario.fim_intervalo = fim_intervalo
        horario.fim = fim

        serializer = self.get_serializer(horario, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

class ItemViewSet(ModelViewSet):
    queryset = ItemEmprestimo.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ItemEmprestimoSerializer

    def list(self, request):
        queryset = self.get_queryset()

        identificador = request.query_params.get('emprestimo', None)

        try:
            emprestimo = Emprestimo.objects.get(identificador=identificador)
        except Emprestimo.DoesNotExist:
            return Response({'detail': 'Não há um empréstimo com esse ID'})

        if emprestimo:
            queryset = queryset.filter(emprestimo=emprestimo.pk)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['patch'], url_path='return')
    def devolver(self, request, *args, **kwargs):

        emprestimo = request.data.get('emprestimo', None)
        nome = request.data.get('nome', None)

        if not emprestimo:
            return Response({'detail': 'Empréstimo não encontrado.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            equipamento = Equipamento.objects.get(patrimonio=nome)
        except Equipamento.DoesNotExist:
            pass

        try:
            obj_nome = ItemEmprestimo.objects.filter(
                emprestimo=emprestimo, nome=nome, devolvido=False
            ).exists()

            if obj_nome:
                obj = ItemEmprestimo.objects.get(
                    emprestimo=emprestimo, nome=nome, devolvido=False
                )
                data = request.data
            else:
                obj = ItemEmprestimo.objects.get(
                    emprestimo=emprestimo, equipamento=equipamento, devolvido=False
                )
                data = { 'emprestimo': emprestimo, 'equipamento': equipamento.pk }
        except ItemEmprestimo.DoesNotExist:
            return Response({'detail': 'Acesso não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        obj.recebente = request.user
        obj.devolucao = timezone.now()
        obj.devolvido = True
        obj.save()

        serializer = self.get_serializer(obj, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

class ManutencaoViewSet(ModelViewSet):
    queryset = Manutencao.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ManutencaoSerializer

    def list(self, request):
        queryset = self.get_queryset()

        patrimonio = request.query_params.get('patrimonio', None)

        try:
            equipamento = Equipamento.objects.get(patrimonio=patrimonio)
        except Equipamento.DoesNotExist:
            return Response({'detail': 'Não há um equipamento com esse nome'})

        if patrimonio:
            queryset = queryset.filter(equipamento=equipamento).reverse()

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):

        descricao = request.data.get('descricao')
        patrimonio = request.data.get('patrimonio')

        try:
            equipamento = Equipamento.objects.get(patrimonio=patrimonio)
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

class OrcamentoViewSet(ModelViewSet):
    queryset = Orcamento.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = OrcamentoSerializer

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
