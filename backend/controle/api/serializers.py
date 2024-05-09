from rest_framework import filters
from rest_framework.serializers import ModelSerializer

from root.models import Pessoa, Sala
from controle.models import ControleAcesso


class PessoaSerializer(ModelSerializer):
    queryset = Pessoa.objects.all()
    serializer_class = Pessoa
    filter_backends = [filters.SearchFilter]
    search_fields = ['matricula']
    class Meta:
        model = Pessoa
        fields = ['id', 'nome', 'email', 'telefone', 'matricula', 'tipo']

class SalaSerializer(ModelSerializer):
    queryset = Sala.objects.all()
    serializer_class = Sala
    filter_backends = [filters.SearchFilter]
    search_fields =  ['numero']
    class Meta:
        model = Sala
        fields = ['id', 'predio', 'nome', 'numero']


class ControleAcessoSerializer(ModelSerializer):
    queryset = ControleAcesso.objects.all()
    serializer_class = ControleAcesso
    filter_backends = [filters.SearchFilter]
    search_fields =  ['hora_saida']
    class Meta:
        model = ControleAcesso
        fields = ['pessoa', 'sala', 'hora_entrada', 'hora_saida']
