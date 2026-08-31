from django.db import models


class Cliente(models.Model):
    """Representa un cliente de la casa de cambio, con su segmentación comercial."""

    class Segmentacion(models.TextChoices):
        MINORISTA = 'MIN', 'Minorista'
        MAYORISTA = 'MAY', 'Mayorista'
        CORPORATIVO = 'COR', 'Corporativo'
        VIP = 'VIP', 'VIP'

    nombre = models.CharField(max_length=150)
    documento_ruc = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    segmentacion = models.CharField(
        max_length=3,
        choices=Segmentacion.choices,
        default=Segmentacion.MINORISTA,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f'{self.nombre} ({self.get_segmentacion_display()})'