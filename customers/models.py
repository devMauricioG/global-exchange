"""
Módulo de modelos para la aplicación de gestión de clientes (customers).

Este módulo define la entidad principal :class:`Cliente` y sus enumeraciones
asociadas para la clasificación y segmentación de clientes en la plataforma
Global Exchange.
"""

from django.db import models


class Cliente(models.Model):
    """
    Modelo representativo de un Cliente dentro del sistema Global Exchange.

    Almacena los datos personales, fiscales, de contacto y clasificación por segmento
    financiero/operativo del cliente.

    :ivar id: Identificador numérico único auto-incremental (clave primaria).
    :vartype id: int
    :ivar nombre: Nombre completo o razón social del cliente.
    :vartype nombre: str
    :ivar documento_ruc: Documento de identidad civil o RUC (único en el sistema).
    :vartype documento_ruc: str
    :ivar correo: Dirección de correo electrónico de contacto (único en el sistema).
    :vartype correo: str
    :ivar telefono: Número telefónico de contacto del cliente (opcional).
    :vartype telefono: str
    :ivar segmentacion: Categoría de segmentación del cliente ('MIN', 'MAY', 'COR', 'VIP').
    :vartype segmentacion: str
    :ivar is_active: Bandera lógica que indica si el cliente está activo o dado de baja.
    :vartype is_active: bool
    :ivar created_at: Fecha y hora de registro del cliente en el sistema.
    :vartype created_at: datetime.datetime
    :ivar updated_at: Fecha y hora de la última actualización de los datos del cliente.
    :vartype updated_at: datetime.datetime
    """

    class Segmentacion(models.TextChoices):
        """
        Opciones de segmentación disponibles para clasificar a los clientes.

        * ``MINORISTA`` ('MIN'): Cliente persona física o minorista estándar.
        * ``MAYORISTA`` ('MAY'): Cliente con perfil mayorista comercial.
        * ``CORPORATIVO`` ('COR'): Empresas e instituciones corporativas.
        * ``VIP`` ('VIP'): Clientes preferenciales o de alto volumen.
        """
        MINORISTA = 'MIN', 'Minorista'
        MAYORISTA = 'MAY', 'Mayorista'
        CORPORATIVO = 'COR', 'Corporativo'
        VIP = 'VIP', 'VIP'

    nombre = models.CharField(
        max_length=150,
        verbose_name='Nombre o Razón Social',
        help_text='Nombre y apellido o razón social de la entidad cliente.',
    )
    documento_ruc = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Documento / RUC',
        help_text='Número de documento de identidad fiscal o civil único.',
    )
    correo = models.EmailField(
        unique=True,
        verbose_name='Correo Electrónico',
        help_text='Dirección de correo electrónico única para notificaciones.',
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Teléfono',
        help_text='Número de teléfono de contacto (opcional).',
    )
    segmentacion = models.CharField(
        max_length=3,
        choices=Segmentacion.choices,
        default=Segmentacion.MINORISTA,
        verbose_name='Segmentación',
        help_text='Categoría o segmento comercial asignado al cliente.',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Indica si el cliente se encuentra actualmente activo en el sistema.',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro',
        help_text='Timestamp automático de creación.',
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización',
        help_text='Timestamp automático de la última modificación.',
    )

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-created_at']

    def __str__(self) -> str:
        """
        Representación en cadena de texto del cliente.

        :return: Nombre del cliente junto con la etiqueta legible de su segmentación.
        :rtype: str
        """
        return f'{self.nombre} ({self.get_segmentacion_display()})'
