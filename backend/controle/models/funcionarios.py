from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint


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
