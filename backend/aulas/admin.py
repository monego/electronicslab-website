from django.contrib import admin
from aulas.models import Aula


class AulaAdmin(admin.ModelAdmin):
    list_display = ('disciplina', 'professor', 'sala', 'inicio', 'fim')

admin.site.register(Aula, AulaAdmin)
