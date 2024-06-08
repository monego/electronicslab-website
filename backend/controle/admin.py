from django.contrib import admin
from controle.models import (
    Atividades,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    Manutencao,
)

class AtividadesAdmin(admin.ModelAdmin):
    list_display = (
        "descricao",
        "estado",
        "hora_iniciada",
        "hora_concluida",
    )
    filter_horizontal = ('funcionarios',)

class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'foto', 'manual')
    search_fields = ('nome', 'descricao')

class EmprestimosAdmin(admin.ModelAdmin):
    list_display = ('responsavel', 'funcionario', 'local', 'retirada', 'devolucao')
    search_fields = ('responsavel', 'local')

class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'funcionario', 'descricao', 'data')
    search_fields = ('equipamento', 'funcionario')

class ControleAcessoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'sala')


admin.site.register(Atividades, AtividadesAdmin)
admin.site.register(ControleAcesso, ControleAcessoAdmin)
admin.site.register(Emprestimo, EmprestimosAdmin)
admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(Manutencao, ManutencaoAdmin)
