from django import forms
from .models import Cliente


class ClienteForm(forms.ModelForm):
    """
    Formulario para la creación y edición de Clientes.
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
    Formulario para filtrar clientes por segmento, búsqueda por documento/nombre y estado.
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
