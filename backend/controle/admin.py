import django_filters
from django.contrib import admin
from django.contrib.auth.models import User
from controle.models import (
    Atividades,
    Ausencia,
    ControleAcesso,
    Emprestimo,
    Equipamento,
    HorarioTrabalho,
    Manutencao,
    Orcamento,
    RegistroPreco,
)

class AtividadesFilter(django_filters.FilterSet):
    grupos = django_filters.ModelMultipleChoiceFilter(queryset=User.objects.all())

class AtividadesAdmin(admin.ModelAdmin):
    list_filter = ('funcionarios', 'estado', 'hora_iniciada', 'hora_concluida',)
    list_display = (
        'descricao',
        'estado',
        'hora_iniciada',
        'hora_concluida',
    )
    filter_horizontal = ('funcionarios',)

class AusenciaAdmin(admin.ModelAdmin):
    list_display = ('funcionario', 'inicio', 'fim', 'motivo')
    search_fields = ('funcionario',)

class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'foto', 'manual')
    search_fields = ('nome', 'descricao')

class EmprestimosAdmin(admin.ModelAdmin):
    list_display = ('responsavel', 'funcionario', 'local', 'retirada', 'devolucao')
    search_fields = ('responsavel', 'local')

class HorarioTrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        'funcionario',
        'dia_da_semana',
        'inicio',
        'fim',
        'inicio_intervalo',
        'fim_intervalo',
    )
    search_fields = ('funcionario',)


class ManutencaoAdmin(admin.ModelAdmin):
    list_display = ('equipamento', 'funcionario', 'descricao', 'data')
    search_fields = ('equipamento', 'funcionario')

class ControleAcessoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'sala')

class RegistroPrecoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'estado')

class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('registro', 'preco')

admin.site.register(Atividades, AtividadesAdmin)
admin.site.register(Ausencia, AusenciaAdmin)
admin.site.register(ControleAcesso, ControleAcessoAdmin)
admin.site.register(Emprestimo, EmprestimosAdmin)
admin.site.register(Equipamento, EquipamentoAdmin)
admin.site.register(HorarioTrabalho, HorarioTrabalhoAdmin)
admin.site.register(Manutencao, ManutencaoAdmin)
admin.site.register(Orcamento, OrcamentoAdmin)
admin.site.register(RegistroPreco, RegistroPrecoAdmin)
