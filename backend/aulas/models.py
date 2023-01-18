from django.db import models
from django.utils.translation import gettext_lazy as _
from controle.models import Pessoa, Laboratorio
from django.utils import timezone

# Create your models here.

class Disciplina(models.Model):
    codigo = models.CharField("Código", max_length=10)
    nome = models.CharField("Nome", max_length=100)


class Status(models.Model):
    descricao = models.CharField(max_length=15)


class Software(models.Model):
    nome = models.CharField(max_length=50)
    versao = models.CharField(max_length=10)
    categoria = models.CharField(max_length=30, null=True)


class SoftwaresLaboratorio(models.Model):
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.SET_NULL, null=True)
    software = models.ForeignKey(Software, on_delete=models.SET_NULL, null=True)


class Aula(models.Model):

    class Status(models.TextChoices):
        ATIVA = 'AT', _('Ativa')
        CANCELADA = 'CL', _('Cancelada')
        PENDENTE = 'PD', _('Pendente')
    
    data = models.DateField()
    hora_inicial = models.DateTimeField(default=timezone.now)
    hora_final = models.DateTimeField(default=timezone.now)
    professor = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.SET_NULL, null=True)
    observacao = models.CharField(max_length=30, null=True)
    arquivo = models.FileField(upload_to='uploads/', null=True)
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.PENDENTE,
    )
