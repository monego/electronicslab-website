from django.db import models
from root.models import Pessoa, Laboratorio
from django.utils import timezone

# Create your models here.

class Setores(models.Model):
    nome = models.CharField(max_length=10)


class Equipamento(models.Model):
    nome = models.CharField(max_length=50, default="Nome")
    descricao = models.CharField(max_length=200, default="Descrição")
    foto = models.ImageField(upload_to ='fotos', null=True)
    manual = models.FileField(upload_to="manuais", null=True)


class LocalEquipamento(models.Model):
    data_atualizacao = models.DateTimeField(default=timezone.now)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True)


class Responsavel(models.Model):
    data_atualizacao = models.DateTimeField(default=timezone.now)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True)
    responsavel = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = "Responsáveis"


class Emprestimo(models.Model):
    responsavel = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True, related_name='interessado')
    funcionario = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True, related_name='funcionario')
    devolucao = models.DateTimeField(default=timezone.now, null=True)
    data_emprestimo = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = "Empréstimos"


class EmprestimoEquipamento(models.Model):
    emprestimo = models.ForeignKey(Emprestimo, on_delete=models.SET_NULL, null=True)
    equipamento = models.ForeignKey(Equipamento, on_delete=models.SET_NULL, null=True)
    descricao_equipamento = models.CharField(max_length=50)
