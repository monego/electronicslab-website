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
    fonte_orcamento_1 = models.CharField(max_length=10, choices=[('website', 'Website'), ('telefone', 'Telefone'), ('email', 'E-mail')], default='website')
    url_orcamento_1 = models.CharField(max_length=300, blank=True, null=True)
    preco_orcamento_1 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    empresa_orcamento_1 = models.CharField(max_length=100, blank=True, null=True)
    data_orcamento_1 = models.DateField(blank=True, null=True)

    fonte_orcamento_2 = models.CharField(max_length=10, choices=[('website', 'Website'), ('telefone', 'Telefone'), ('email', 'E-mail')], default='website')
    url_orcamento_2 = models.CharField(max_length=300, blank=True, null=True)
    preco_orcamento_2 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    empresa_orcamento_2 = models.CharField(max_length=100, blank=True, null=True)
    data_orcamento_2 = models.DateField(blank=True, null=True)

    fonte_orcamento_3 = models.CharField(max_length=10, choices=[('website', 'Website'), ('telefone', 'Telefone'), ('email', 'E-mail')], default='website')
    url_orcamento_3 = models.CharField(max_length=300, blank=True, null=True)
    preco_orcamento_3 = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    empresa_orcamento_3 = models.CharField(max_length=100, blank=True, null=True)
    data_orcamento_3 = models.DateField(blank=True, null=True)

    preco_maximo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)


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
