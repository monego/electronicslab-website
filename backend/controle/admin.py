from django.contrib import admin
from controle.models import ControleAcesso

# Register your models here.

class ControleAcessoAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'sala')


admin.site.register(ControleAcesso, ControleAcessoAdmin)
