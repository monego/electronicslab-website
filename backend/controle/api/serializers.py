import rest_framework.serializers as serializers
from controle.models import (
    Ausencia,
    Compras,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    HorarioTrabalho,
    ItemEmprestimo,
    Manutencao,
    Orcamento,
)

class AusenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ausencia
        fields = '__all__'

class ComprasSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.SerializerMethodField()

    class Meta:
        model = Compras
        fields = [
            "id",
            "data",
            "titulo",
            "descricao",
            "quantidade",
            "justificativa",
            "estado",
            "origem",
            "tipo",
            "funcionario_nome",
            "url_orcamento_1",
            "fonte_orcamento_1",
            "preco_orcamento_1",
            "empresa_orcamento_1",
            "data_orcamento_1",
            "url_orcamento_2",
            "fonte_orcamento_2",
            "preco_orcamento_2",
            "empresa_orcamento_2",
            "data_orcamento_2",
            "url_orcamento_3",
            "fonte_orcamento_3",
            "preco_orcamento_3",
            "empresa_orcamento_3",
            "data_orcamento_3",
            "preco_maximo",
        ]

    def get_funcionario_nome(self, obj):
        if fun := obj.funcionario:
            return f"{fun.first_name} {fun.last_name}"
        else:
            return

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

class ItemEmprestimoSerializer(serializers.ModelSerializer):
    equipamento_nome = serializers.StringRelatedField(
        source="equipamento.nome", read_only=True
    )
    equipamento_patrimonio = serializers.StringRelatedField(
        source="equipamento.patrimonio", read_only=True
    )
    recebente_nome = serializers.SerializerMethodField()

    def get_recebente_nome(self, obj):
        if fun := obj.recebente:
            return f"{fun.first_name} {fun.last_name}"
        else:
            return

    class Meta:
        model = ItemEmprestimo
        fields = [
            "emprestimo",
            "equipamento",
            "nome",
            "devolvido",
            "devolucao",
            "recebente_nome",
            "equipamento_nome",
            "equipamento_patrimonio",
        ]

class EmprestimoSerializer(serializers.ModelSerializer):
    responsavel_nome = serializers.SerializerMethodField()
    responsavel_matricula = serializers.SerializerMethodField()
    funcionario_nome = serializers.SerializerMethodField()
    items_nomes = serializers.SerializerMethodField()

    class Meta:
        model = Emprestimo
        fields = [
            "identificador",
            "items_nomes",
            "funcionario_nome",
            "responsavel_nome",
            "responsavel_matricula",
            "local",
            "encerrado",
            "retirada",
        ]

    def get_responsavel_nome(self, obj):
        return obj.responsavel.nome if obj.responsavel else None

    def get_responsavel_matricula(self, obj):
        return obj.responsavel.matricula if obj.responsavel else None

    def get_funcionario_nome(self, obj):
        if fun := obj.funcionario:
            return f"{fun.first_name} {fun.last_name}"
        else:
            return

    def get_items_nomes(self, obj):
        items = ItemEmprestimo.objects.filter(emprestimo=obj)
        item_names = []
        for item in items:
            if not item.equipamento:
                item_names.append(item.nome)
            else:
                item_names.append(item.equipamento.nome)
        return '; '.join(item_names)


class EquipamentoSerializer(serializers.ModelSerializer):
    num_manutencao = serializers.IntegerField(read_only=True)
    num_emprestimo = serializers.IntegerField(read_only=True)
    sala_numero = serializers.SerializerMethodField()

    class Meta:
        model = Equipamento
        fields = ['nome', 'descricao', 'patrimonio', 'sala', 'sala_numero',
                  'defeito', 'foto', 'manual', 'num_manutencao', 'num_emprestimo']

    def get_sala_numero(self, obj):
        return obj.sala.numero if obj.sala else None

class EquipamentoPublicoSerializer(serializers.ModelSerializer):
    sala_numero = serializers.SerializerMethodField()

    class Meta:
        model = Equipamento
        fields = ['nome', 'patrimonio', 'sala_numero', 'foto', 'manual']

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

class OrcamentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Orcamento
        fields = '__all__'
