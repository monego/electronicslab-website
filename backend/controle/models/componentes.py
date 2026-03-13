from django.db import models

class Componente(models.Model):

    class Categoria(models.TextChoices):
        ELETRICA = 'Elétrica'
        PNEUMATICA = 'Pneumática'
        PROCESSOS = 'Processos'

    class Tipo(models.TextChoices):
        RESISTOR = 'Resistor'
        POTENCIOMETRO = 'Potenciômetro'
        CAPACITOR = 'Capacitor'
        INDUTOR = 'Indutor'
        CIRCUITO_LOGICO = 'CI Lógico'
        CIRCUITO_INTEGRADO = 'CI'
        TRANSISTOR = 'Transistor'
        MOSFET = 'MOSFET'
        IGBT = 'IGBT'
        TRIAC = 'TRIAC'
        DIAC = 'DIAC'
        SEMICONDUTOR = 'Semicondutor'
        REGULADOR = 'Regulador'
        OPAMP = 'OpAmp'
        DIODO = 'Diodo'
        LED = 'LED'
        SENSOR = 'Sensor'
        SHIELD = 'Shield'
        MICROCONTROLADOR = 'Microcontrolador'
        CABO = 'Cabo'
        MODULO = 'Módulo'
        COMPONENTE = 'Componente'
        OUTRO = 'Outro'

    nome = models.CharField(max_length=35, default="")
    descricao = models.CharField(max_length=100, default="")
    quantidade = models.PositiveSmallIntegerField()
    datasheet = models.FileField(blank=True, null=True)
    categoria = models.CharField(
        max_length=15,
        choices=Categoria.choices,
        default=Categoria.ELETRICA,
    )
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.OUTRO,
    )

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ["nome", "tipo"]
