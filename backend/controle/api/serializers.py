from rest_framework import filters
import rest_framework.serializers as serializers
from controle.models import (
    Atividades,
    Ausencia,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    HorarioTrabalho,
    Manutencao,
)

class AtividadesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Atividades
        fields = '__all__'

class AusenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ausencia
        fields = '__all__'

class ControleAcessoSerializer(serializers.ModelSerializer):
    queryset = ControleAcesso.objects.all()
    serializer_class = ControleAcesso
    filter_backends = [filters.SearchFilter]
    search_fields =  ['id']

    class Meta:
        model = ControleAcesso
        fields = ['id', 'pessoa', 'sala', 'hora_entrada', 'hora_saida']

class EmprestimoSerializer(serializers.ModelSerializer):

    queryset = Emprestimo.objects.all()
    serializer_class = Emprestimo
    filter_backends = [filters.SearchFilter]
    search_fields =  ['responsavel']

    items = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )

    class Meta:
        model = Emprestimo
        fields = '__all__'
        depth = 1

class EquipamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Equipamento
        fields = '__all__'

class HorarioTrabalhoSerializer(serializers.ModelSerializer):

    class Meta:
        model = HorarioTrabalho
        fields = '__all__'

class ManutencaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manutencao
        fields = '__all__'
