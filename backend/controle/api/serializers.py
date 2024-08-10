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
from root.models import Pessoa, Sala

class AtividadesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Atividades
        fields = '__all__'

class AusenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ausencia
        fields = '__all__'

class ControleAcessoSerializer(serializers.ModelSerializer):
    pessoa_nome = serializers.SerializerMethodField()
    pessoa_matricula = serializers.SerializerMethodField()
    sala_numero = serializers.SerializerMethodField()

    class Meta:
        model = ControleAcesso
        fields = '__all__'

    def get_pessoa_nome(self, obj):
        return obj.pessoa.nome if obj.pessoa else None

    def get_pessoa_matricula(self, obj):
        return obj.pessoa.matricula if obj.pessoa else None

    def get_sala_numero(self, obj):
        return obj.sala.numero if obj.sala else None

class EmprestimoSerializer(serializers.ModelSerializer):

    queryset = Emprestimo.objects.all()
    serializer_class = Emprestimo
    filter_backends = [filters.SearchFilter]
    search_fields =  ['id']

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
