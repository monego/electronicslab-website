from django.contrib import admin

# Register your models here.

from .models import Disciplina, Software

admin.site.register(Disciplina)
admin.site.register(Software)