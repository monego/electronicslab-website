from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from root.models import Pessoa, Laboratorio

# Create your models here.


# class Matriculas(models.Model):
#     pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True)
#     matricula = models.CharField(max_length=50)


class ControleBolsistas(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'BO'})
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(default=timezone.now)


class ControleAcesso(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'AL'})
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.SET_NULL, null=True)
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(default=timezone.now)
