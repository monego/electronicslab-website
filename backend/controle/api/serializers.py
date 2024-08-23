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
    responsavel_nome = serializers.SerializerMethodField()
    responsavel_matricula = serializers.SerializerMethodField()
    funcionario_nome = serializers.SerializerMethodField()

    items = serializers.ListField(
        child=serializers.CharField(max_length=200)
    )

    class Meta:
        model = Emprestimo
        fields = '__all__'

    def get_responsavel_nome(self, obj):
        return obj.responsavel.nome if obj.responsavel else None

    def get_responsavel_matricula(self, obj):
        return obj.responsavel.matricula if obj.responsavel else None

    def get_funcionario_nome(self, obj):
        if fun := obj.funcionario:
            return f"{fun.first_name} {fun.last_name}"
        else:
            return

class EquipamentoSerializer(serializers.ModelSerializer):
    num_manutencao = serializers.IntegerField(read_only=True)
    sala_numero = serializers.SerializerMethodField()

    class Meta:
        model = Equipamento
        fields = ['nome', 'descricao', 'patrimonio', 'sala', 'sala_numero',
                  'defeito', 'foto', 'manual', 'num_manutencao']

    def get_sala_numero(self, obj):
        return obj.sala.numero if obj.sala else None

class HorarioTrabalhoSerializer(serializers.ModelSerializer):

    class Meta:
        model = HorarioTrabalho
        fields = '__all__'

class ManutencaoSerializer(serializers.ModelSerializer):
    equipamento_nome = serializers.SerializerMethodField()
    funcionario_nome = serializers.SerializerMethodField()

    class Meta:
        model = Manutencao
        fields = '__all__'

    def get_equipamento_nome(self, obj):
        return obj.equipamento.nome if obj.equipamento else None

    def get_funcionario_nome(self, obj):
        if fun := obj.funcionario:
            return f"{fun.first_name} {fun.last_name}"
        else:
            return
