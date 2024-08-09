from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from root.models import Pessoa, Sala
import uuid


def image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    return f"fotos/{fname}"

def file_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    fname = f"{uuid.uuid4()}.{ext}"
    return f"manuais/{fname}"

class Atividades(models.Model):

    CHOICES = [
        ('waiting', 'Aguardando'),
        ('finished', 'Concluída'),
    ]

    funcionarios = models.ManyToManyField(User, related_name='atividades')
    descricao = models.CharField(max_length=200, default="")
    estado = models.CharField(choices=CHOICES, default="waiting", max_length=15)
    observacao = models.CharField(max_length=150, blank=True)
    hora_iniciada = models.DateTimeField(default=timezone.now)
    hora_concluida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.descricao} - {self.estado}"

    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'

class AtualizacaoAtividade(models.Model):

    CHOICES = [
        ('waiting', 'Aguardando'),
        ('finished', 'Concluída'),
    ]

    atividade = models.ForeignKey(Atividades, on_delete=models.CASCADE)
    observacao = models.CharField(max_length=30, default="")
    data = models.DateTimeField(default=timezone.now)
    estado = models.CharField(choices=CHOICES, default="waiting", max_length=15)

    def save(self, *args, **kwargs):
        if self.estado:
            self.atividade.estado = self.estado
            if self.estado == 'finished':
                self.atividade.hora_concluida = timezone.now()
            self.atividade.save()

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Atualização Atividades'
        verbose_name_plural = 'Atualizações Atividades'

class Ausencia(models.Model):
    funcionario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="absences"
    )
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    motivo = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.funcionario} - {self.reason} ({self.start_datetime} até {self.end_datetime})"

    class Meta:
        verbose_name = 'Ausência'
        verbose_name_plural = 'Ausências'

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
    hora_saida = models.DateTimeField(default=timezone.now)

class Emprestimo(models.Model):
    identificador = models.CharField(max_length=15, default="", unique=True)
    responsavel = models.ForeignKey(
        Pessoa, on_delete=models.SET_NULL, null=True, related_name="responsavel"
    )
    funcionario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="funcionario"
    )
    local = models.CharField(max_length=20, default="")
    items = ArrayField(models.CharField(max_length=20), default=list)
    retirada = models.DateTimeField(default=timezone.now)
    devolucao = models.DateTimeField(default=timezone.now, blank=True, null=True)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = "Empréstimos"

class Equipamento(models.Model):

    CHOICES = [
        ('working', 'Em uso'),
        ('broken', 'Defeito'),
    ]

    nome = models.CharField(max_length=50, default="Nome", unique=True)
    descricao = models.CharField(max_length=200, default="Descrição")
    patrimonio = models.CharField(max_length=15, unique=True, null=True, blank=True)
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True)
    estado = models.CharField(choices=CHOICES, default="working", max_length=15)
    foto = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    manual = models.FileField(upload_to=file_upload_path, blank=True, null=True)

    def __str__(self):
        return self.nome

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


class Manutencao(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=300, default="")
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'

class RegistroPreco(models.Model):
    nome = models.CharField(max_length=50)
    descricao = models.CharField(max_length=1000)
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=[
        ('solicitado', 'Solicitado'),
        ('aprovado', 'Aprovado'),
        ('tramitado', 'Tramitado'),
        ('comprado', 'Comprado'),
        ('recebido', 'Recebido'),
    ])
    justificativa = models.CharField(max_length=1000)
    origem = models.CharField(max_length=20, choices=[
        ('almoxarifado', 'Almoxarifado'),
        ('cartaocorporativo', 'Cartão Corporativo'),
        ('registrodepreco', 'Registro de Preço'),
    ])
    tipo = models.CharField(max_length=15, choices=[
        ('permanente', 'Permanente'),
        ('consumo', 'Consumo'),
    ])
    solicitante = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Registro de Preço'
        verbose_name_plural = 'Registros de Preço'

class Orcamento(models.Model):
    registro = models.ForeignKey(RegistroPreco, on_delete=models.CASCADE)
    empresa = models.CharField(max_length=50)
    data = models.DateTimeField(default=timezone.now)
    preco = models.CharField(max_length=15)

    class Meta:
        verbose_name = 'Orçamento'
        verbose_name_plural = 'Orçamentos'
