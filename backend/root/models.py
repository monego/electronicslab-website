from django.db import models

# Create your models here.

class Pessoa(models.Model):

    class Tipo(models.TextChoices):
        ALUNO = 'AL'
        BOLSISTA = 'BO'
        FUNCIONARIO = 'FU'
        PROFESSOR = 'PR'

    nome = models.CharField(max_length=100, default="")
    email = models.CharField(max_length=50, null=True)
    telefone = models.CharField(max_length=20, null=True)
    matricula = models.CharField(max_length=50, default="", unique=True)
    tipo = models.CharField(
        max_length=2,
        choices=Tipo.choices,
        default=Tipo.ALUNO,
    )

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome", "tipo"]


class Predio(models.Model):
    nome = models.CharField(max_length=100, default="")
    numero = models.CharField(max_length=10, default="")

    def __str__(self):
        return self.numero + " - " + self.nome

    class Meta:
        verbose_name = 'Prédio'
        verbose_name_plural = "Prédios"


class Sala(models.Model):
    predio = models.ForeignKey(Predio, on_delete=models.SET_NULL, null=True)
    nome = models.CharField(max_length=50, null=True)
    numero = models.CharField(max_length=5, null=True)
    andar = models.SmallIntegerField(choices=[
        (1, '1'),
        (2, '2')
    ], default=1)
    codigo = models.CharField(max_length=5, null=True)
    imagem = models.ImageField("Imagem", null=True, blank=True)

    def __str__(self):
        return "[" + self.numero + "]" + " " + self.nome

    class Meta:
        ordering = ["numero"]

