from django.contrib import admin

# Register your models here.

from .models import (Equipamento)

class EquipamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao', 'foto', 'manual')
    search_fields = ('nome', 'descricao')

admin.site.register(Equipamento, EquipamentoAdmin)