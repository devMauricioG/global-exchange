"""
Módulo de formularios para la aplicación de clientes.

Contiene las clases de formulario Django utilizadas tanto para la creación y edición
de entidades :class:`~customers.models.Cliente` como para el filtrado avanzado
y búsqueda en los listados web.
"""

from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """
    Formulario basado en modelo (:class:`django.forms.ModelForm`) para crear y editar clientes.

    Aplica estilos visuales específicos a través de atributos HTML de clase (`form-input`, `form-select`, etc.)
    y asegura la captura de datos con validaciones estándar de Django.

    :cvar model: Modelo de referencia (:class:`~customers.models.Cliente`).
    :cvar fields: Lista de campos gestionados en el formulario.
    """

    class Meta:
        model = Cliente
        fields = [
            'nombre',
            'documento_ruc',
            'correo',
            'telefono',
            'segmentacion',
            'is_active',
        ]
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Ej. Juan Pérez o Empresa S.A.',
                    'required': True,
                }
            ),
            'documento_ruc': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Ej. 1234567-8 o CI/RUC',
                    'required': True,
                }
            ),
            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'cliente@ejemplo.com',
                    'required': True,
                }
            ),
            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Ej. +595 981 123456',
                }
            ),
            'segmentacion': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
            'is_active': forms.CheckboxInput(
                attrs={
                    'class': 'form-checkbox',
                }
            ),
        }
        labels = {
            'nombre': 'Nombre o Razón Social',
            'documento_ruc': 'Documento / RUC',
            'correo': 'Correo Electrónico',
            'telefono': 'Teléfono de Contacto',
            'segmentacion': 'Segmentación',
            'is_active': 'Cliente Activo',
        }


class ClienteFilterForm(forms.Form):
    """
    Formulario de filtrado y búsqueda para el listado de clientes.

    Permite a los usuarios filtrar registros por segmento comercial, estado de actividad,
    documento fiscal/civil exacto o realizar búsquedas textuales amplias.

    :ivar q: Término de búsqueda general (coincidencia en nombre, RUC, email o teléfono).
    :vartype q: django.forms.CharField
    :ivar segmentacion: Opción seleccionada del catálogo de segmentación.
    :vartype segmentacion: django.forms.ChoiceField
    :ivar documento_ruc: Filtro de documento o RUC.
    :vartype documento_ruc: django.forms.CharField
    :ivar is_active: Filtro por estado del cliente ('true', 'false' o '' para todos).
    :vartype is_active: django.forms.ChoiceField
    """

    q = forms.CharField(
        required=False,
        label='Búsqueda',
        widget=forms.TextInput(
            attrs={
                'class': 'filter-input',
                'placeholder': 'Buscar por nombre, RUC, correo o teléfono...',
            }
        ),
    )
    segmentacion = forms.ChoiceField(
        required=False,
        label='Segmento',
        choices=[('', 'Todos los segmentos')] + list(Cliente.Segmentacion.choices),
        widget=forms.Select(
            attrs={
                'class': 'filter-select',
            }
        ),
    )
    documento_ruc = forms.CharField(
        required=False,
        label='Documento/RUC exacto',
        widget=forms.TextInput(
            attrs={
                'class': 'filter-input',
                'placeholder': 'Filtrar por RUC/Doc exacto...',
            }
        ),
    )
    is_active = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[
            ('', 'Todos'),
            ('true', 'Activos'),
            ('false', 'Inactivos'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'filter-select',
            }
        ),
    )
