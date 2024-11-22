from django.db import models
from root.models import Sala

class Aula(models.Model):
    inicio = models.DateTimeField()
    fim = models.DateTimeField()
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE, null=True, default=None)
    professor = models.CharField(max_length = 100, default="")
    disciplina = models.CharField(max_length = 100, default="")

    class Meta:
        ordering = ['inicio']
        constraints = [
            models.UniqueConstraint(
                fields=["inicio", "fim", "sala"], name="unique_aula"
            )
        ]
