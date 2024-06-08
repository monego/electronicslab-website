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
        ('started', 'Iniciada'),
        ('finished', 'Concluída'),
    ]

    funcionarios = models.ManyToManyField(User, related_name='atividades')
    descricao = models.CharField(max_length=200, default="")
    estado = models.CharField(choices=CHOICES, default="waiting", max_length=15)
    hora_iniciada = models.DateTimeField(default=timezone.now)
    hora_concluida = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Atividade'
        verbose_name_plural = 'Atividades'

class ControleAcesso(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'AL'})
    sala = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True)
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Registro'
        verbose_name_plural = 'Registros'

class ControleBolsistas(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'BO'})
    hora_entrada = models.DateTimeField(default=timezone.now)
    hora_saida = models.DateTimeField(default=timezone.now)

class Emprestimo(models.Model):
    responsavel = models.ForeignKey(
        Pessoa, on_delete=models.SET_NULL, null=True, related_name="responsavel"
    )
    funcionario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="funcionario"
    )
    # equipamento = models.ManyToManyField(Equipamento)
    local = models.CharField(max_length=20, default="")
    items = ArrayField(models.CharField(max_length=20), default=list)
    retirada = models.DateTimeField(default=timezone.now)
    devolucao = models.DateTimeField(default=timezone.now, blank=True, null=True)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = "Empréstimos"

    def save(self, *args, **kwargs):
        if not self.created_by:  # Only set if it's not already set
            user = getattr(self, '_user', None)
            if user and isinstance(user, User):
                self.funcionario = (
                    f"{user.first_name} {user.last_name}"
                    if user.first_name or user.last_name
                    else ""
                )
            else:
                self.funcionario = ""
        super().save(*args, **kwargs)

class Equipamento(models.Model):
    nome = models.CharField(max_length=50, default="Nome", unique=True)
    descricao = models.CharField(max_length=200, default="Descrição")
    patrimonio = models.CharField(max_length=15, null=True, blank=True)
    foto = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    manual = models.FileField(upload_to=file_upload_path, blank=True, null=True)

    def __str__(self):
        return self.nome


    class Meta:
        verbose_name = 'Equipamento'
        verbose_name_plural = 'Equipamentos'

class Manutencao(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=300, default="")
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
