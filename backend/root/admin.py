from django.contrib import admin

# Register your models here.

from .models import (Laboratorio, Pessoa, Predio, Sala)

class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'matricula', 'tipo')
    search_fields = ('nome', 'matricula')

    def tipo(self, obj):
        if obj.tipo == "AL":
            return "Aluno"
        elif obj.tipo == "BO":
            return "Bolsista"
        elif obj.tipo == "FU":
            return "Funcionário"
        elif obj.tipo == "PR":
            return "Professor"
        else:
            pass


class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')


class PredioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'numero')


class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'predio', 'numero')


admin.site.register(Laboratorio, LaboratorioAdmin)
admin.site.register(Pessoa, PessoaAdmin)
admin.site.register(Predio, PredioAdmin)
admin.site.register(Sala, SalaAdmin)
