import json
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Cliente

User = get_user_model()


class ClienteModelTests(TestCase):
    """Pruebas unitarias para el modelo Cliente."""

    def test_cliente_creation(self):
        cliente = Cliente.objects.create(
            nombre='Acme Corporation',
            documento_ruc='80012345-6',
            correo='contacto@acme.com',
            telefono='+595 21 123456',
            segmentacion=Cliente.Segmentacion.CORPORATIVO,
        )
        self.assertEqual(cliente.nombre, 'Acme Corporation')
        self.assertEqual(cliente.segmentacion, 'COR')
        self.assertTrue(cliente.is_active)
        self.assertEqual(str(cliente), 'Acme Corporation (Corporativo)')

    def test_cliente_default_values(self):
        cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento_ruc='1234567',
            correo='juan@correo.com',
        )
        self.assertEqual(cliente.segmentacion, Cliente.Segmentacion.MINORISTA)
        self.assertTrue(cliente.is_active)
        self.assertEqual(str(cliente), 'Juan Pérez (Minorista)')

    def test_cliente_unique_documento_ruc(self):
        Cliente.objects.create(
            nombre='Cliente 1',
            documento_ruc='111111-1',
            correo='cliente1@test.com',
        )
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                nombre='Cliente 2',
                documento_ruc='111111-1',
                correo='cliente2@test.com',
            )

    def test_cliente_unique_correo(self):
        Cliente.objects.create(
            nombre='Cliente A',
            documento_ruc='222222-1',
            correo='duplicado@test.com',
        )
        with self.assertRaises(IntegrityError):
            Cliente.objects.create(
                nombre='Cliente B',
                documento_ruc='333333-1',
                correo='duplicado@test.com',
            )


class ClienteWebViewsTests(TestCase):
    """Pruebas de vistas basadas en clases (CBVs) para la interfaz web."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='operador',
            email='operador@globalexchange.com',
            password='Password123!',
        )
        self.client_auth = Client()
        self.client_auth.force_login(self.user)

        self.c_min = Cliente.objects.create(
            nombre='Carlos Minorista',
            documento_ruc='1001-MIN',
            correo='carlos@min.com',
            telefono='0981111111',
            segmentacion=Cliente.Segmentacion.MINORISTA,
            is_active=True,
        )
        self.c_may = Cliente.objects.create(
            nombre='Distribuidora Mayorista S.A.',
            documento_ruc='2002-MAY',
            correo='ventas@mayorista.com',
            telefono='0982222222',
            segmentacion=Cliente.Segmentacion.MAYORISTA,
            is_active=True,
        )
        self.c_cor = Cliente.objects.create(
            nombre='Banco Corporativo S.A.',
            documento_ruc='3003-COR',
            correo='contacto@corporativo.com',
            telefono='0983333333',
            segmentacion=Cliente.Segmentacion.CORPORATIVO,
            is_active=False,
        )
        self.c_vip = Cliente.objects.create(
            nombre='Inversiones VIP',
            documento_ruc='4004-VIP',
            correo='ceo@vip.com',
            telefono='0984444444',
            segmentacion=Cliente.Segmentacion.VIP,
            is_active=True,
        )

    def test_list_view_login_required(self):
        unauthenticated_client = Client()
        response = unauthenticated_client.get(reverse('customers:cliente-list'))
        self.assertEqual(response.status_code, 302)

    def test_list_view_authenticated(self):
        response = self.client_auth.get(reverse('customers:cliente-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Minorista')
        self.assertContains(response, 'Distribuidora Mayorista S.A.')
        self.assertContains(response, 'Banco Corporativo S.A.')
        self.assertContains(response, 'Inversiones VIP')

    def test_list_view_filter_by_segmentation(self):
        # Filtro MIN
        response = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'segmentacion': 'MIN'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Minorista')
        self.assertNotContains(response, 'Distribuidora Mayorista S.A.')
        self.assertNotContains(response, 'Inversiones VIP')

        # Filtro VIP
        response_vip = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'segmentacion': 'VIP'}
        )
        self.assertEqual(response_vip.status_code, 200)
        self.assertContains(response_vip, 'Inversiones VIP')
        self.assertNotContains(response_vip, 'Carlos Minorista')

    def test_list_view_filter_by_documento_ruc(self):
        response = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'documento_ruc': '2002-MAY'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Distribuidora Mayorista S.A.')
        self.assertNotContains(response, 'Carlos Minorista')

    def test_list_view_search_q(self):
        # Búsqueda por término parcial en nombre
        response = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'q': 'Banco'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Banco Corporativo S.A.')
        self.assertNotContains(response, 'Carlos Minorista')

        # Búsqueda por teléfono
        response_tel = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'q': '0984444444'}
        )
        self.assertEqual(response_tel.status_code, 200)
        self.assertContains(response_tel, 'Inversiones VIP')

    def test_list_view_filter_by_is_active(self):
        response_inactive = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'is_active': 'false'}
        )
        self.assertEqual(response_inactive.status_code, 200)
        self.assertContains(response_inactive, 'Banco Corporativo S.A.')
        self.assertNotContains(response_inactive, 'Carlos Minorista')

    def test_detail_view(self):
        response = self.client_auth.get(
            reverse('customers:cliente-detail', kwargs={'pk': self.c_vip.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inversiones VIP')
        self.assertContains(response, '4004-VIP')
        self.assertContains(response, 'ceo@vip.com')

    def test_create_view_get(self):
        response = self.client_auth.get(reverse('customers:cliente-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nuevo Cliente')

    def test_create_view_post_success(self):
        payload = {
            'nombre': 'Nuevo Cliente Prueba',
            'documento_ruc': '999999-9',
            'correo': 'nuevo@cliente.com',
            'telefono': '0985555555',
            'segmentacion': 'COR',
            'is_active': True,
        }
        response = self.client_auth.post(reverse('customers:cliente-create'), data=payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Cliente.objects.filter(documento_ruc='999999-9').exists())

    def test_create_view_post_duplicate_error(self):
        payload = {
            'nombre': 'Cliente Duplicado',
            'documento_ruc': self.c_min.documento_ruc,
            'correo': 'otro@correo.com',
            'telefono': '098111',
            'segmentacion': 'MIN',
        }
        response = self.client_auth.post(reverse('customers:cliente-create'), data=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_update_view(self):
        payload = {
            'nombre': 'Carlos Minorista Actualizado',
            'documento_ruc': self.c_min.documento_ruc,
            'correo': 'carlos_nuevo@min.com',
            'telefono': '0989999999',
            'segmentacion': 'MAY',
            'is_active': True,
        }
        response = self.client_auth.post(
            reverse('customers:cliente-update', kwargs={'pk': self.c_min.pk}),
            data=payload
        )
        self.assertEqual(response.status_code, 302)
        self.c_min.refresh_from_db()
        self.assertEqual(self.c_min.nombre, 'Carlos Minorista Actualizado')
        self.assertEqual(self.c_min.segmentacion, 'MAY')

    def test_delete_view(self):
        pk = self.c_min.pk
        response = self.client_auth.post(
            reverse('customers:cliente-delete', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cliente.objects.filter(pk=pk).exists())


class ClienteAPIEndpointsTests(TestCase):
    """Pruebas de endpoints API REST (JSON) para Clientes."""

    def setUp(self):
        self.c1 = Cliente.objects.create(
            nombre='Tech Solutions',
            documento_ruc='12345-1',
            correo='info@tech.com',
            telefono='021123456',
            segmentacion=Cliente.Segmentacion.CORPORATIVO,
            is_active=True,
        )
        self.c2 = Cliente.objects.create(
            nombre='Kiosko Central',
            documento_ruc='67890-2',
            correo='kiosko@central.com',
            telefono='021654321',
            segmentacion=Cliente.Segmentacion.MINORISTA,
            is_active=False,
        )

    def test_api_list_clients(self):
        response = self.client.get(reverse('customers:api-cliente-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['results']), 2)

    def test_api_filter_by_segmentation(self):
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'segmentacion': 'COR'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['nombre'], 'Tech Solutions')
        self.assertEqual(data['results'][0]['segmentacion_display'], 'Corporativo')

    def test_api_filter_by_documento_ruc(self):
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'documento_ruc': '67890-2'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['nombre'], 'Kiosko Central')

    def test_api_filter_by_search_q(self):
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'q': 'kiosko'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['documento_ruc'], '67890-2')

    def test_api_filter_by_is_active(self):
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'is_active': 'true'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['nombre'], 'Tech Solutions')

    def test_api_create_client_success(self):
        payload = {
            'nombre': 'Supermercado El Sol',
            'documento_ruc': '55555-5',
            'correo': 'contacto@elsol.com',
            'telefono': '0981999888',
            'segmentacion': 'MAY',
            'is_active': True,
        }
        response = self.client.post(
            reverse('customers:api-cliente-list-create'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['cliente']['nombre'], 'Supermercado El Sol')
        self.assertEqual(data['cliente']['segmentacion'], 'MAY')
        self.assertTrue(Cliente.objects.filter(documento_ruc='55555-5').exists())

    def test_api_create_client_validation_error(self):
        payload = {
            'nombre': 'Cliente Invalido',
            'documento_ruc': self.c1.documento_ruc,  # RUC duplicado
            'correo': 'correo_invalido',  # Email inválido
            'segmentacion': 'XYZ',  # Segmento inválido
        }
        response = self.client.post(
            reverse('customers:api-cliente-list-create'),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('details', data)

    def test_api_create_client_invalid_json(self):
        response = self.client.post(
            reverse('customers:api-cliente-list-create'),
            data='{invalid_json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_api_get_detail_by_id(self):
        response = self.client.get(
            reverse('customers:api-cliente-detail', kwargs={'pk': self.c1.pk})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.c1.pk)
        self.assertEqual(data['nombre'], 'Tech Solutions')

    def test_api_get_detail_by_documento_ruc(self):
        response = self.client.get(
            reverse('customers:api-cliente-by-doc', kwargs={'documento_ruc': self.c1.documento_ruc})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['documento_ruc'], self.c1.documento_ruc)

    def test_api_get_detail_not_found(self):
        response = self.client.get(
            reverse('customers:api-cliente-detail', kwargs={'pk': 999999})
        )
        self.assertEqual(response.status_code, 404)

    def test_api_update_put(self):
        payload = {
            'nombre': 'Tech Solutions S.A.',
            'documento_ruc': self.c1.documento_ruc,
            'correo': 'nuevo_tech@tech.com',
            'telefono': '021999999',
            'segmentacion': 'VIP',
            'is_active': True,
        }
        response = self.client.put(
            reverse('customers:api-cliente-detail', kwargs={'pk': self.c1.pk}),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.nombre, 'Tech Solutions S.A.')
        self.assertEqual(self.c1.segmentacion, 'VIP')

    def test_api_update_patch(self):
        payload = {
            'telefono': '0987111222',
            'segmentacion': 'VIP',
        }
        response = self.client.patch(
            reverse('customers:api-cliente-detail', kwargs={'pk': self.c1.pk}),
            data=json.dumps(payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.c1.refresh_from_db()
        self.assertEqual(self.c1.telefono, '0987111222')
        self.assertEqual(self.c1.segmentacion, 'VIP')
        self.assertEqual(self.c1.nombre, 'Tech Solutions')  # Nombre original intacto

    def test_api_delete(self):
        pk = self.c1.pk
        response = self.client.delete(
            reverse('customers:api-cliente-detail', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cliente.objects.filter(pk=pk).exists())
