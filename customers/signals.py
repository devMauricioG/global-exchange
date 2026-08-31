"""
Módulo de señales y receptores (Signals) para la aplicación de clientes.

Intercepta los eventos de autenticación exitosa tanto a través de la señal nativa de Django
:data:`django.contrib.auth.signals.user_logged_in` como mediante la señal personalizada
:data:`keycloak_user_authenticated` para coordinar la vinculación automática
con la ficha de cliente (:class:`~customers.models.Cliente`).
"""

import logging
from typing import Any, Dict, Optional

from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.signals import user_logged_in
from django.dispatch import Signal, receiver
from django.http import HttpRequest

from .services import vincular_cliente_keycloak

logger = logging.getLogger(__name__)

# Señal personalizada emitida al autenticar o refrescar un usuario vía Keycloak OIDC
keycloak_user_authenticated = Signal()
"""
Señal emitida cuando un usuario es autenticado exitosamente mediante Keycloak OIDC.

:param sender: Clase emisora o backend de autenticación.
:param user: Instancia del usuario Django autenticado (:class:`django.contrib.auth.models.User`).
:param claims: Diccionario de claims decodificadas de Keycloak.
:param keycloak_id: Identificador universal ``sub`` del usuario en Keycloak.
:param request: Objeto de solicitud HTTP actual (opcional).
"""


@receiver(keycloak_user_authenticated)
def handle_keycloak_user_authenticated(
    sender: Any,
    user: AbstractBaseUser,
    claims: Optional[Dict[str, Any]] = None,
    keycloak_id: Optional[str] = None,
    request: Optional[HttpRequest] = None,
    **kwargs: Any,
) -> None:
    """
    Receptor que procesa la señal personalizada :data:`keycloak_user_authenticated`.

    Ejecuta el servicio :func:`~customers.services.vincular_cliente_keycloak`
    garantizando que la ficha de cliente quede vinculada inmediatamente con el ``sub``
    y los datos del token de Keycloak.

    :param sender: Origen de la señal.
    :param user: Usuario autenticado en Django.
    :type user: django.contrib.auth.models.AbstractBaseUser
    :param claims: Diccionario de claims OIDC.
    :type claims: dict, optional
    :param keycloak_id: Identificador ``sub`` de Keycloak.
    :type keycloak_id: str, optional
    :param request: Solicitud HTTP asociada.
    :type request: django.http.HttpRequest, optional
    """
    if claims is None:
        claims = {}
    sub = keycloak_id or claims.get("sub")
    email = claims.get("email") or getattr(user, "email", "")

    logger.debug(
        "Señal keycloak_user_authenticated recibida para usuario=%s, sub=%s",
        getattr(user, "username", str(user)),
        sub,
    )
    vincular_cliente_keycloak(
        user=user,
        keycloak_id=sub,
        email=email,
        claims=claims,
    )


@receiver(user_logged_in)
def handle_django_user_logged_in(
    sender: Any,
    request: HttpRequest,
    user: AbstractBaseUser,
    **kwargs: Any,
) -> None:
    """
    Receptor conectado a la señal estándar :data:`django.contrib.auth.signals.user_logged_in`.

    Se dispara en cada inicio de sesión exitoso. Si el usuario cuenta con correo electrónico
    o ficha previa, asegura la consistencia de la vinculación entre el usuario Django y el cliente.

    :param sender: Clase emisora de la señal.
    :param request: Objeto HttpRequest de la petición de login.
    :type request: django.http.HttpRequest
    :param user: Instancia del usuario que inició sesión.
    :type user: django.contrib.auth.models.AbstractBaseUser
    """
    email = getattr(user, "email", "")
    logger.debug(
        "Señal user_logged_in recibida para usuario=%s (email=%s)",
        getattr(user, "username", str(user)),
        email,
    )
    if email:
        vincular_cliente_keycloak(
            user=user,
            email=email,
        )
