"""
Módulo de pruebas automatizadas para la aplicación de clientes.

Contiene las suites de pruebas unitarias y de integración para validar el modelo
:class:`~customers.models.Cliente`, las vistas web basadas en clases (CBVs)
y los endpoints de la API REST (JSON).
"""

import json
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Cliente

User = get_user_model()


class ClienteModelTests(TestCase):
    """
    Suite de pruebas unitarias para el modelo :class:`~customers.models.Cliente`.

    Verifica la instanciación de entidades, asignación de valores por defecto,
    métodos de representación y restricciones de unicidad en la base de datos.
    """

    def test_cliente_creation(self):
        """Valida la creación exitosa de un cliente con todos sus campos y segmentación."""
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
        """Verifica que los valores por defecto (segmentación MINORISTA y activo True) se asignen correctamente."""
        cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            documento_ruc='1234567',
            correo='juan@correo.com',
        )
        self.assertEqual(cliente.segmentacion, Cliente.Segmentacion.MINORISTA)
        self.assertTrue(cliente.is_active)
        self.assertEqual(str(cliente), 'Juan Pérez (Minorista)')

    def test_cliente_unique_documento_ruc(self):
        """Asegura que no sea posible registrar dos clientes con el mismo documento/RUC."""
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
        """Asegura que no sea posible registrar dos clientes con la misma dirección de correo electrónico."""
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
    """
    Suite de pruebas para las vistas basadas en clases (CBVs) de la interfaz web de clientes.

    Cubre el acceso autenticado, renderizado de listados, filtros por segmento y RUC,
    búsqueda general y operaciones CRUD mediante formularios web.
    """

    def setUp(self):
        """Inicializa el entorno de prueba creando un usuario autenticado y un catálogo diverso de clientes."""
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
        """Verifica que un usuario no autenticado sea redirigido al intentar acceder al listado de clientes."""
        unauthenticated_client = Client()
        response = unauthenticated_client.get(reverse('customers:cliente-list'))
        self.assertEqual(response.status_code, 302)

    def test_list_view_authenticated(self):
        """Verifica que un usuario autenticado pueda visualizar el listado completo de clientes."""
        response = self.client_auth.get(reverse('customers:cliente-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Carlos Minorista')
        self.assertContains(response, 'Distribuidora Mayorista S.A.')
        self.assertContains(response, 'Banco Corporativo S.A.')
        self.assertContains(response, 'Inversiones VIP')

    def test_list_view_filter_by_segmentation(self):
        """Verifica que el filtrado por código de segmentación (MIN, VIP) devuelva únicamente los registros coincidentes."""
        response_min = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'segmentacion': 'MIN'}
        )
        self.assertEqual(response_min.status_code, 200)
        self.assertContains(response_min, 'Carlos Minorista')
        self.assertNotContains(response_min, 'Distribuidora Mayorista S.A.')
        self.assertNotContains(response_min, 'Inversiones VIP')

        response_vip = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'segmentacion': 'VIP'}
        )
        self.assertEqual(response_vip.status_code, 200)
        self.assertContains(response_vip, 'Inversiones VIP')
        self.assertNotContains(response_vip, 'Carlos Minorista')

    def test_list_view_filter_by_documento_ruc(self):
        """Verifica el filtrado exacto o parcial por el campo documento_ruc."""
        response = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'documento_ruc': '2002-MAY'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Distribuidora Mayorista S.A.')
        self.assertNotContains(response, 'Carlos Minorista')

    def test_list_view_search_q(self):
        """Verifica la búsqueda abierta por texto 'q' sobre el nombre o teléfono del cliente."""
        response = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'q': 'Banco'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Banco Corporativo S.A.')
        self.assertNotContains(response, 'Carlos Minorista')

        response_tel = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'q': '0984444444'}
        )
        self.assertEqual(response_tel.status_code, 200)
        self.assertContains(response_tel, 'Inversiones VIP')

    def test_list_view_filter_by_is_active(self):
        """Verifica el filtrado según el estado de actividad (is_active=false)."""
        response_inactive = self.client_auth.get(
            reverse('customers:cliente-list'),
            {'is_active': 'false'}
        )
        self.assertEqual(response_inactive.status_code, 200)
        self.assertContains(response_inactive, 'Banco Corporativo S.A.')
        self.assertNotContains(response_inactive, 'Carlos Minorista')

    def test_detail_view(self):
        """Verifica el renderizado de la vista de detalle de un cliente."""
        response = self.client_auth.get(
            reverse('customers:cliente-detail', kwargs={'pk': self.c_vip.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Inversiones VIP')
        self.assertContains(response, '4004-VIP')
        self.assertContains(response, 'ceo@vip.com')

    def test_create_view_get(self):
        """Verifica que la petición GET al formulario de creación devuelva código 200."""
        response = self.client_auth.get(reverse('customers:cliente-create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nuevo Cliente')

    def test_create_view_post_success(self):
        """Verifica la creación exitosa de un cliente a través del formulario web."""
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
        """Verifica el manejo de errores de validación al intentar registrar un documento duplicado."""
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
        """Verifica la actualización de los datos de un cliente mediante el formulario de edición."""
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
        """Verifica la eliminación definitiva de un cliente tras confirmar la acción en la vista de borrado."""
        pk = self.c_min.pk
        response = self.client_auth.post(
            reverse('customers:cliente-delete', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Cliente.objects.filter(pk=pk).exists())


class ClienteAPIEndpointsTests(TestCase):
    """
    Suite de pruebas para los endpoints de la API REST (JSON) de Clientes.

    Cubre operaciones de listado, filtros, creación (POST), consulta por PK y por RUC,
    actualizaciones totales (PUT) y parciales (PATCH), y borrado (DELETE).
    """

    def setUp(self):
        """Prepara datos iniciales de prueba para las llamadas API."""
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
        """Verifica que el endpoint GET /customers/api/ devuelva todos los clientes en formato JSON."""
        response = self.client.get(reverse('customers:api-cliente-list-create'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['results']), 2)

    def test_api_filter_by_segmentation(self):
        """Verifica el filtrado de clientes en la API por el parámetro ?segmentacion=COR."""
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
        """Verifica el filtrado en la API por el parámetro ?documento_ruc=67890-2."""
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'documento_ruc': '67890-2'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['nombre'], 'Kiosko Central')

    def test_api_filter_by_search_q(self):
        """Verifica la búsqueda general en la API usando el parámetro ?q=kiosko."""
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'q': 'kiosko'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['documento_ruc'], '67890-2')

    def test_api_filter_by_is_active(self):
        """Verifica el filtrado en la API por estado de actividad ?is_active=true."""
        response = self.client.get(
            reverse('customers:api-cliente-list-create'),
            {'is_active': 'true'}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], 1)
        self.assertEqual(data['results'][0]['nombre'], 'Tech Solutions')

    def test_api_create_client_success(self):
        """Verifica la creación de un nuevo cliente vía POST enviando un cuerpo JSON estructurado."""
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
        """Verifica que el envío de datos inválidos (RUC duplicado, segmento erróneo) retorne HTTP 400."""
        payload = {
            'nombre': 'Cliente Invalido',
            'documento_ruc': self.c1.documento_ruc,
            'correo': 'correo_invalido',
            'segmentacion': 'XYZ',
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
        """Verifica que un JSON malformado devuelva HTTP 400 Bad Request."""
        response = self.client.post(
            reverse('customers:api-cliente-list-create'),
            data='{invalid_json',
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)

    def test_api_get_detail_by_id(self):
        """Verifica la recuperación de un cliente individual por su ID (PK)."""
        response = self.client.get(
            reverse('customers:api-cliente-detail', kwargs={'pk': self.c1.pk})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.c1.pk)
        self.assertEqual(data['nombre'], 'Tech Solutions')

    def test_api_get_detail_by_documento_ruc(self):
        """Verifica la recuperación de un cliente individual utilizando su documento_ruc."""
        response = self.client.get(
            reverse('customers:api-cliente-by-doc', kwargs={'documento_ruc': self.c1.documento_ruc})
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['documento_ruc'], self.c1.documento_ruc)

    def test_api_get_detail_not_found(self):
        """Verifica que la consulta de un cliente inexistente devuelva HTTP 404 Not Found."""
        response = self.client.get(
            reverse('customers:api-cliente-detail', kwargs={'pk': 999999})
        )
        self.assertEqual(response.status_code, 404)

    def test_api_update_put(self):
        """Verifica la actualización completa de un cliente mediante el método HTTP PUT."""
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
        """Verifica la actualización parcial de atributos de un cliente mediante el método HTTP PATCH."""
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
        self.assertEqual(self.c1.nombre, 'Tech Solutions')

    def test_api_delete(self):
        """Verifica la eliminación de un cliente a través del endpoint HTTP DELETE."""
        pk = self.c1.pk
        response = self.client.delete(
            reverse('customers:api-cliente-detail', kwargs={'pk': pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Cliente.objects.filter(pk=pk).exists())


class ClienteKeycloakVinculationTests(TestCase):
    """
    Suite de pruebas para la lógica de vinculación automática de identidades Keycloak (claim sub).
    """

    def setUp(self):
        """Inicializa usuarios y fichas de prueba."""
        self.user = User.objects.create_user(
            username='carlos_kc',
            email='carlos.keycloak@globalexchange.com',
            first_name='Carlos',
            last_name='Keycloak',
            password='Password123!',
        )
        self.sub_uuid = 'f47ac10b-58cc-4372-a567-0e02b2c3d479'

    def test_vincular_cliente_por_sub_existente(self):
        """Verifica que si ya existe un cliente con el sub registrado, se asocie con el usuario."""
        cliente_previo = Cliente.objects.create(
            nombre='Carlos Previo',
            documento_ruc='99999-1',
            correo='carlos.previo@test.com',
            keycloak_id=self.sub_uuid,
        )
        from customers.services import vincular_cliente_keycloak

        cliente = vincular_cliente_keycloak(
            user=self.user,
            keycloak_id=self.sub_uuid,
            email='carlos.keycloak@globalexchange.com',
        )

        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.pk, cliente_previo.pk)
        self.assertEqual(cliente.keycloak_id, self.sub_uuid)
        self.assertEqual(cliente.usuario, self.user)

    def test_vincular_cliente_por_correo_existente(self):
        """Verifica que una ficha existente creada por un admin se vincule automáticamente por email."""
        cliente_admin = Cliente.objects.create(
            nombre='Carlos Registrado Previamente',
            documento_ruc='88888-2',
            correo='carlos.keycloak@globalexchange.com',
            keycloak_id=None,
            usuario=None,
        )
        from customers.services import vincular_cliente_keycloak

        cliente = vincular_cliente_keycloak(
            user=self.user,
            keycloak_id=self.sub_uuid,
            email='carlos.keycloak@globalexchange.com',
        )

        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.pk, cliente_admin.pk)
        self.assertEqual(cliente.keycloak_id, self.sub_uuid)
        self.assertEqual(cliente.usuario, self.user)

    def test_crear_y_vincular_cliente_automatico(self):
        """Verifica que se cree una nueva ficha de cliente automáticamente si no existía previamente."""
        from customers.services import vincular_cliente_keycloak

        nuevo_user = User.objects.create_user(
            username='nuevo_cliente',
            email='nuevo.cliente@globalexchange.com',
            first_name='Ana',
            last_name='Gómez',
        )
        nuevo_sub = 'a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d'
        claims = {
            'sub': nuevo_sub,
            'email': 'nuevo.cliente@globalexchange.com',
            'given_name': 'Ana',
            'family_name': 'Gómez',
            'preferred_username': 'nuevo_cliente',
        }

        cliente = vincular_cliente_keycloak(
            user=nuevo_user,
            keycloak_id=nuevo_sub,
            claims=claims,
        )

        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.nombre, 'Ana Gómez')
        self.assertEqual(cliente.correo, 'nuevo.cliente@globalexchange.com')
        self.assertEqual(cliente.keycloak_id, nuevo_sub)
        self.assertEqual(cliente.usuario, nuevo_user)
        self.assertTrue(cliente.is_active)

    def test_signal_keycloak_user_authenticated_dispatched(self):
        """Verifica que al emitir la señal keycloak_user_authenticated se ejecute la vinculación."""
        from customers.signals import keycloak_user_authenticated

        signal_sub = 'signal-sub-uuid-1234'
        keycloak_user_authenticated.send(
            sender=self.__class__,
            user=self.user,
            keycloak_id=signal_sub,
            claims={'sub': signal_sub, 'email': self.user.email},
        )

        cliente = Cliente.objects.filter(keycloak_id=signal_sub).first()
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.usuario, self.user)

    def test_signal_user_logged_in_triggers_vinculation(self):
        """Verifica que la señal nativa user_logged_in sincronice la ficha existente."""
        from django.contrib.auth.signals import user_logged_in
        from django.test import RequestFactory

        cliente_existente = Cliente.objects.create(
            nombre='Usuario Logeado',
            documento_ruc='77777-3',
            correo='login.test@globalexchange.com',
        )
        login_user = User.objects.create_user(
            username='login_user',
            email='login.test@globalexchange.com',
        )
        factory = RequestFactory()
        request = factory.get('/')

        user_logged_in.send(
            sender=login_user.__class__,
            request=request,
            user=login_user,
        )

        cliente_existente.refresh_from_db()
        self.assertEqual(cliente_existente.usuario, login_user)

