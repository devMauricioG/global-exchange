import json
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ClienteFilterForm, ClienteForm
from .models import Cliente


def _serialize_cliente(cliente: Cliente) -> dict:
    """Función auxiliar para serializar una instancia de Cliente a diccionario JSON."""
    return {
        'id': cliente.id,
        'nombre': cliente.nombre,
        'documento_ruc': cliente.documento_ruc,
        'correo': cliente.correo,
        'telefono': cliente.telefono,
        'segmentacion': cliente.segmentacion,
        'segmentacion_display': cliente.get_segmentacion_display(),
        'is_active': cliente.is_active,
        'created_at': cliente.created_at.isoformat() if cliente.created_at else None,
        'updated_at': cliente.updated_at.isoformat() if cliente.updated_at else None,
    }


# ==============================================================================
# VISTAS BASADAS EN CLASES (CBV) - INTERFAZ WEB
# ==============================================================================

class ClienteListView(LoginRequiredMixin, ListView):
    """
    Lista clientes con soporte para filtrado por segmento, búsqueda por documento,
    búsqueda por texto y filtrado por estado activo/inactivo.
    """
    model = Cliente
    template_name = 'customers/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 10

    def get_queryset(self):
        queryset = Cliente.objects.all().order_by('-created_at')
        self.filter_form = ClienteFilterForm(self.request.GET)

        if self.filter_form.is_valid():
            q = self.filter_form.cleaned_data.get('q')
            segmentacion = self.filter_form.cleaned_data.get('segmentacion')
            documento_ruc = self.filter_form.cleaned_data.get('documento_ruc')
            is_active = self.filter_form.cleaned_data.get('is_active')

            if segmentacion:
                queryset = queryset.filter(segmentacion=segmentacion)

            if documento_ruc:
                queryset = queryset.filter(documento_ruc__icontains=documento_ruc)

            if q:
                queryset = queryset.filter(
                    Q(nombre__icontains=q)
                    | Q(documento_ruc__icontains=q)
                    | Q(correo__icontains=q)
                    | Q(telefono__icontains=q)
                )

            if is_active == 'true':
                queryset = queryset.filter(is_active=True)
            elif is_active == 'false':
                queryset = queryset.filter(is_active=False)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(self, 'filter_form', ClienteFilterForm(self.request.GET))
        context['segment_choices'] = Cliente.Segmentacion.choices
        context['total_count'] = Cliente.objects.count()
        context['active_count'] = Cliente.objects.filter(is_active=True).count()
        
        # Mantener parámetros de búsqueda en la paginación
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        context['querystring'] = query_params.urlencode()
        return context


class ClienteDetailView(LoginRequiredMixin, DetailView):
    """Vista de detalle de un cliente."""
    model = Cliente
    template_name = 'customers/cliente_detail.html'
    context_object_name = 'cliente'


class ClienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """Vista para la creación de un nuevo cliente."""
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente-list')
    success_message = 'Cliente "%(nombre)s" registrado exitosamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Crear'
        context['title'] = 'Nuevo Cliente'
        return context


class ClienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """Vista para la actualización de datos de un cliente existente."""
    model = Cliente
    form_class = ClienteForm
    template_name = 'customers/cliente_form.html'
    success_url = reverse_lazy('customers:cliente-list')
    success_message = 'Cliente "%(nombre)s" actualizado exitosamente.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Actualizar'
        context['title'] = f'Editar Cliente: {self.object.nombre}'
        return context


class ClienteDeleteView(LoginRequiredMixin, DeleteView):
    """Vista para la confirmación y eliminación de un cliente."""
    model = Cliente
    template_name = 'customers/cliente_confirm_delete.html'
    context_object_name = 'cliente'
    success_url = reverse_lazy('customers:cliente-list')

    def post(self, request, *args, **kwargs):
        cliente = self.get_object()
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f'Cliente "{nombre}" eliminado exitosamente.')
        return redirect(self.success_url)


# ==============================================================================
# API VIEWS (ENDPOINTS REST / JSON)
# ==============================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ClienteListCreateAPIView(View):
    """
    Endpoint API REST para listar y crear clientes.
    - GET /customers/api/
        Parámetros query soportados:
        - segmentacion: Código del segmento (MIN, MAY, COR, VIP)
        - documento_ruc: Búsqueda exacta o parcial por RUC/documento
        - q: Búsqueda general por nombre, documento, correo o teléfono
        - is_active: 'true' o 'false'
        - page: Número de página (opcional, 20 items por pág)
    - POST /customers/api/
        Crea un nuevo cliente con el payload JSON proporcionado.
    """

    def get(self, request):
        queryset = Cliente.objects.all().order_by('-created_at')

        segmentacion = request.GET.get('segmentacion', '').strip()
        documento_ruc = request.GET.get('documento_ruc', '').strip()
        q = request.GET.get('q', '').strip()
        is_active = request.GET.get('is_active', '').strip().lower()

        if segmentacion:
            queryset = queryset.filter(segmentacion=segmentacion)

        if documento_ruc:
            queryset = queryset.filter(documento_ruc__icontains=documento_ruc)

        if q:
            queryset = queryset.filter(
                Q(nombre__icontains=q)
                | Q(documento_ruc__icontains=q)
                | Q(correo__icontains=q)
                | Q(telefono__icontains=q)
            )

        if is_active in ['true', '1']:
            queryset = queryset.filter(is_active=True)
        elif is_active in ['false', '0']:
            queryset = queryset.filter(is_active=False)

        # Paginación opcional
        page = request.GET.get('page')
        if page:
            paginator = Paginator(queryset, 20)
            page_obj = paginator.get_page(page)
            results = [_serialize_cliente(c) for c in page_obj]
            return JsonResponse({
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'results': results,
            })

        results = [_serialize_cliente(c) for c in queryset]
        return JsonResponse({'count': len(results), 'results': results}, safe=False)

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Payload JSON inválido.'},
                status=400
            )

        form = ClienteForm(data)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse(
                {
                    'message': 'Cliente creado exitosamente.',
                    'cliente': _serialize_cliente(cliente),
                },
                status=201
            )
        else:
            return JsonResponse(
                {
                    'error': 'Error de validación.',
                    'details': form.errors.get_json_data(),
                },
                status=400
            )


@method_decorator(csrf_exempt, name='dispatch')
class ClienteDetailAPIView(View):
    """
    Endpoint API REST para obtener, actualizar y eliminar un cliente por PK o por documento_ruc.
    - GET /customers/api/<pk>/ o /customers/api/documento/<documento_ruc>/
    - PUT / PATCH /customers/api/<pk>/
    - DELETE /customers/api/<pk>/
    """

    def _get_object(self, pk=None, documento_ruc=None):
        if pk is not None:
            return get_object_or_404(Cliente, pk=pk)
        elif documento_ruc is not None:
            return get_object_or_404(Cliente, documento_ruc=documento_ruc)
        raise Http404('Cliente no encontrado.')

    def get(self, request, pk=None, documento_ruc=None):
        cliente = self._get_object(pk=pk, documento_ruc=documento_ruc)
        return JsonResponse(_serialize_cliente(cliente))

    def put(self, request, pk=None, documento_ruc=None):
        cliente = self._get_object(pk=pk, documento_ruc=documento_ruc)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Payload JSON inválido.'}, status=400)

        form = ClienteForm(data, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse(
                {
                    'message': 'Cliente actualizado exitosamente.',
                    'cliente': _serialize_cliente(cliente),
                },
                status=200
            )
        else:
            return JsonResponse(
                {
                    'error': 'Error de validación.',
                    'details': form.errors.get_json_data(),
                },
                status=400
            )

    def patch(self, request, pk=None, documento_ruc=None):
        cliente = self._get_object(pk=pk, documento_ruc=documento_ruc)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Payload JSON inválido.'}, status=400)

        # Construir datos existentes mezclados con los nuevos
        current_data = {
            'nombre': cliente.nombre,
            'documento_ruc': cliente.documento_ruc,
            'correo': cliente.correo,
            'telefono': cliente.telefono,
            'segmentacion': cliente.segmentacion,
            'is_active': cliente.is_active,
        }
        current_data.update(data)

        form = ClienteForm(current_data, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse(
                {
                    'message': 'Cliente actualizado exitosamente.',
                    'cliente': _serialize_cliente(cliente),
                },
                status=200
            )
        else:
            return JsonResponse(
                {
                    'error': 'Error de validación.',
                    'details': form.errors.get_json_data(),
                },
                status=400
            )

    def delete(self, request, pk=None, documento_ruc=None):
        cliente = self._get_object(pk=pk, documento_ruc=documento_ruc)
        cliente_id = cliente.id
        cliente.delete()
        return JsonResponse(
            {'message': f'Cliente con ID {cliente_id} eliminado exitosamente.'},
            status=200
        )
