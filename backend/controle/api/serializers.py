from rest_framework import filters
from rest_framework.serializers import ModelSerializer
from controle.models import (
    Atividades,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    Manutencao,
)

class AtividadesSerializer(ModelSerializer):

    class Meta:
        model = Atividades
        fields = '__all__'

class ControleAcessoSerializer(ModelSerializer):
    queryset = ControleAcesso.objects.all()
    serializer_class = ControleAcesso
    filter_backends = [filters.SearchFilter]
    search_fields =  ['id']

    class Meta:
        model = ControleAcesso
        fields = ['id', 'pessoa', 'sala', 'hora_entrada', 'hora_saida']

class EmprestimoSerializer(ModelSerializer):

    class Meta:
        model = Emprestimo
        fields = '__all__'

class EquipamentoSerializer(ModelSerializer):

    class Meta:
        model = Equipamento
        fields = '__all__'

class ManutencaoSerializer(ModelSerializer):

    class Meta:
        model = Manutencao
        fields = '__all__'
