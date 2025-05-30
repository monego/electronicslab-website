from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Compras(models.Model):
    data = models.DateTimeField(default=timezone.now)
    titulo = models.CharField(max_length=100, default="")
    descricao = models.TextField(max_length=500)
    quantidade = models.PositiveSmallIntegerField()
    justificativa = models.TextField(max_length=500)
    estado = models.CharField(max_length=15, choices=[
        ('solicitado', 'Solicitado'),
        ('aprovado', 'aprovado'),
        ('tramitado', 'Tramitado'),
        ('comprado', 'Comprado'),
        ('recebido', 'Recebido'),
        ('negado', 'Negado'),
        ('excluido', 'Excluído')
    ],
    default = 'solicitado'
    )
    origem = models.CharField(max_length=25, choices=[
        ('almox', 'Almoxarifado'),
        ('cc', 'Cartão Corporativo'),
        ('rp', 'Registro de Preço')
    ])
    tipo = models.CharField(max_length=15, choices=[
        ('permanente', 'Permanente'),
        ('consumo', 'Consumo')
    ])
    funcionario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='solicitante'
    )

    def __str__(self):
        return f"{self.titulo}"

    class Meta:
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

class Orcamento(models.Model):
    compra = models.ForeignKey(Compras, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=25)
    data = models.DateField()
    preco = models.DecimalField(max_digits=6, decimal_places=2)
    website = models.URLField(max_length=200)
    anexo = models.FileField()

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
