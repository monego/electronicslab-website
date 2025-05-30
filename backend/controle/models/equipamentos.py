from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from PIL import Image
from root.models import Sala
import io
import os


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

class Manutencao(models.Model):
    equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(User, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=300, default="")
    data = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Manutenção'
        verbose_name_plural = 'Manutenções'
