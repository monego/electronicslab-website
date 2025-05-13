from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from root.models import Pessoa, Sala
from PIL import Image
import io
import os

class Ausencia(models.Model):
    funcionario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="absences"
    )
    inicio = models.DateField()
    fim = models.DateField()
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.funcionario} - {self.motivo} ({self.inicio} até {self.fim})"

    class Meta:
        verbose_name = 'Ausência'
        verbose_name_plural = 'Ausências'

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

class ControleAcesso(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'AL'})
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True)
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.pessoa} - {self.sala}"

    class Meta:
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'

class ControleBolsistas(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'BO'})
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(blank=True, null=True)

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

class Equipamento(models.Model):

    CHOICES = [
        ('working', 'Em uso'),
        ('broken', 'Defeito'),
    ]

    nome = models.CharField(max_length=200, default="Nome")
    descricao = models.CharField(max_length=200, default="Descrição")
    patrimonio = models.CharField(max_length=15, unique=True, default="SP")
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True, blank=True)
    defeito = models.BooleanField(default=False)
    foto = models.ImageField(blank=True, null=True)
    manual = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        """ Optimize image by converting to WebP, 80% quality """

        if self.foto:
            foto_webp = Image.open(self.foto)

            orig_path = self.foto.path

            foto_io = io.BytesIO()

            foto_webp.save(foto_io, format='WebP', quality=80)

            foto_file = ContentFile(
                foto_io.getvalue(),
                name=f"{os.path.splitext(self.foto.name)[0]}.webp"
            )

            self.foto.save(foto_file.name, foto_file, save=False)

            super().save(*args, **kwargs)

            # Remove the original, unoptimized image
            if os.path.exists(orig_path):
                os.remove(orig_path)

    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

class HorarioTrabalho(models.Model):
    funcionario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="work_schedules"
    )
    dia_da_semana = models.CharField(max_length=10, choices=[
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
    ])
    inicio = models.TimeField()
    fim = models.TimeField()
    inicio_intervalo = models.TimeField(null=True, blank=True)
    fim_intervalo = models.TimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Horário de Trabalho'
        verbose_name_plural = 'Horários de Trabalho'
        constraints = [
            UniqueConstraint(fields=['funcionario', 'dia_da_semana'], name='jornada'),
        ]

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

class Manutencao(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=300, default="")
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'

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
