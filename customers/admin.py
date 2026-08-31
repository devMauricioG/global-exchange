from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'documento_ruc',
        'correo',
        'telefono',
        'segmentacion',
        'is_active',
        'created_at',
    )
    list_filter = ('segmentacion', 'is_active', 'created_at')
    search_fields = ('nombre', 'documento_ruc', 'correo', 'telefono')
    ordering = ('-created_at',)
    list_editable = ('segmentacion', 'is_active')
