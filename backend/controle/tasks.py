from django.utils import timezone
from datetime import timedelta
from controle.models import ControleAcesso


def registrar_saida_automatica():
    """
    Registra a saída automática de pessoas que entraram há mais de 4 horas
    e não tiveram sua saída registrada.
    """
    limite = timezone.now() - timedelta(hours=4)
    registros_pendentes = ControleAcesso.objects.filter(
        hora_saida__isnull=True,
        hora_entrada__lt=limite
    )

    count = registros_pendentes.count()
    for registro in registros_pendentes:
        # Define a hora de saída como 4 horas após o horário de entrada
        registro.hora_saida = registro.hora_entrada + timedelta(hours=4)
        registro.save()

    return f"Registradas {count} saídas automáticas."
