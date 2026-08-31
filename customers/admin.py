"""
Módulo de administración de Django para la aplicación de clientes.

Registra y personaliza el modelo :class:`~customers.models.Cliente` en el panel de control
de administración de Django con columnas informativas, filtros por segmento y estado,
herramientas de búsqueda y edición rápida.
"""

from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """
    Configuración del panel de administración de Django para el modelo :class:`~customers.models.Cliente`.

    :cvar list_display: Campos visualizados en la tabla del listado de clientes.
    :cvar list_filter: Filtros laterales para segmentación, estado activo y fecha de creación.
    :cvar search_fields: Campos indexados para la barra de búsqueda del panel admin.
    :cvar ordering: Orden de visualización por defecto (fecha de creación descendente).
    :cvar list_editable: Campos editables directamente desde la tabla de listado.
    """

    list_display = (
        'id',
        'nombre',
        'documento_ruc',
        'correo',
        'telefono',
        'segmentacion',
        'keycloak_id',
        'usuario',
        'is_active',
        'created_at',
    )
    list_filter = ('segmentacion', 'is_active', 'created_at')
    search_fields = ('nombre', 'documento_ruc', 'correo', 'telefono', 'keycloak_id', 'usuario__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('segmentacion', 'is_active')
