from .serializers import PessoaSerializer, SalaSerializer
from root.models import Pessoa, Sala
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from django.db.models import Max, F
...
class PessoaViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PessoaSerializer

    def get_queryset(self):
        queryset = Pessoa.objects.annotate(last_access=Max('controleacesso__hora_entrada'))
        matricula = self.request.query_params.get('matricula')
        if matricula is not None:
            queryset = queryset.filter(matricula=matricula)

        nome = self.request.query_params.get('nome')
        if nome is not None:
            queryset = queryset.filter(nome__icontains=nome).order_by(
                F('last_access').desc(nulls_last=True),
                'nome'
            )[:20]

        return queryset

    @action(detail=False, methods=['patch'], url_path='mailphone')
    def patch_mailphone(self, request, *args, **kwargs):
        matricula = request.data.get('matricula', None)
        email = request.data.get('email', None)
        telefone = request.data.get('telefone', None)

        if not matricula:
            return Response({'detail': 'Matrícula do aluno é necessária.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            pessoa = Pessoa.objects.get(matricula=matricula)
        except Pessoa.DoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'},
                            status=status.HTTP_404_NOT_FOUND)

        pessoa.email = email
        pessoa.telefone = telefone

        serializer = self.get_serializer(pessoa, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class SalaViewSet(ModelViewSet):
    permission_classes = []
    serializer_class = SalaSerializer
    queryset = Sala.objects.all()

    def get_queryset(self):
        queryset = Sala.objects.all()
        numero = self.request.query_params.get('numero')
        if numero is not None:
            queryset = queryset.filter(numero=numero)
        return queryset
