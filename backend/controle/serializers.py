from rest_framework.serializers import ModelSerializer

from root.models import Pessoa, Sala, Laboratorio
from .models import ControleAcesso

class PessoaSerializer(ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ['nome', 'matricula', 'tipo']

class SalaSerializer(ModelSerializer):
    class Meta:
        model = Sala
        fields = ['nome', 'numero']

class LaboratorioSerializer(ModelSerializer):
    class Meta:
        model = Laboratorio
        fields = ['sala']

class ControleAcessoSerializer(ModelSerializer):
#    Pessoas = PessoaSerializer(source='pessoa', required=False)
#    Salas = SalaSerializer(source='sala', required=False)
    class Meta:
        model = ControleAcesso
        fields = ['hora_entrada']
        #fields = ['pessoa', 'laboratorio', 'hora_entrada', 'hora_saida']
