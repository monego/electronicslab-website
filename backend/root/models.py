from django.db import models

# Create your models here.

class Pessoa(models.Model):

    class Tipo(models.TextChoices):
        ALUNO = 'AL'
        BOLSISTA = 'BO'
        FUNCIONARIO = 'FU'
        PROFESSOR = 'PR'

    nome = models.CharField(max_length=100, default="")
    email = models.CharField(max_length=50, null=True, default="")
    telefone = models.CharField(max_length=20, null=True, default="")
    matricula = models.CharField(max_length=50, default="")
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
    nome = models.CharField(max_length=50)
    numero = models.CharField(max_length=5)

    def __str__(self):
        return "[" + self.numero + "]" + " " + self.nome

    class Meta:
        ordering = ["numero"]


class Laboratorio(models.Model):
    nome = models.ForeignKey(Sala, on_delete=models.SET_NULL, null=True)
    imagem = models.ImageField("Imagem")
    ativo = models.BooleanField()

    class Meta:
        ordering = ["nome"]
        verbose_name = 'Laboratório'
        verbose_name_plural = "Laboratórios"


class Professores(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.SET_NULL, null=True,
                               limit_choices_to={'tipo': 'PR'})
    apelido = models.CharField(max_length=15)

    class Meta:
        ordering = ["pessoa"]
        verbose_name = 'Professor'
        verbose_name_plural = "Professores"