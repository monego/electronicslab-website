from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from root.models import Pessoa
from .equipamentos import Equipamento


class Emprestimo(models.Model):
    identificador = models.CharField(max_length=15, default="", unique=True)
    responsavel = models.ForeignKey(
        Pessoa, on_delete=models.SET_NULL, null=True, related_name="responsavel"
    )
    funcionario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="funcionario"
    )
    local = models.CharField(max_length=20, default="")
    retirada = models.DateTimeField(default=timezone.now)
    encerrado = models.BooleanField(default=False)
    devolucao = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.identificador

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = "Empréstimos"

class ItemEmprestimo(models.Model):
    emprestimo = models.ForeignKey(
        Emprestimo, on_delete=models.SET_NULL, null=True, related_name='emprestimo'
    )
    equipamento = models.ForeignKey(
        Equipamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='item_emprestimo',
    )
    nome = models.CharField(max_length=100, blank=True, null=True)
    recebente = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="recebente"
    )
    devolvido = models.BooleanField(default=False)
    devolucao = models.DateTimeField(blank=True, null=True)

    def clean(self):
        if not self.equipamento and not self.nome:
            raise ValidationError('Ao menos "equipamento" ou "nome" deve constar.')
        if self.equipamento is not None and self.nome is not None:
            raise ValidationError('Apenas um entre "equipamento" e "nome" é permitido.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.nome:
            return self.nome
        elif self.equipamento:
            return self.equipamento.nome

    class Meta:
        verbose_name = 'Item de Empréstimo'
        verbose_name_plural = 'Items de Empréstimo'
