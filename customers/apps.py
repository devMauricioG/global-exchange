"""
Configuración de la aplicación de clientes (customers).
"""

from django.apps import AppConfig


class CustomersConfig(AppConfig):
    """
    Clase de configuración para la aplicación ``customers``.

    Registra los receptores de señales para la vinculación automática de identidades Keycloak
    al inicializarse la aplicación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'
    verbose_name = 'Gestión de Clientes'

    def ready(self) -> None:
        """
        Importa y registra las señales de la aplicación al arrancar Django.
        """
        import customers.signals  # noqa: F401

