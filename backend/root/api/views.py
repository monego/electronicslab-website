from .serializers import PessoaSerializer, SalaSerializer
from root.models import Pessoa, Sala
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet


class PessoaViewSet(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = PessoaSerializer

    def get_queryset(self):
        queryset = Pessoa.objects.all()
        matricula = self.request.query_params.get('matricula')
        if matricula is not None:
            queryset = queryset.filter(matricula=matricula)
        return queryset


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
