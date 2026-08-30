"""
Vistas de autenticación para integración con Keycloak OIDC.

Proporciona logout unificado (Django + Keycloak) para SSO completo.
"""

import logging

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class KeycloakLogoutView(View):
    """
    Cierra la sesión de Django y redirige al endpoint de logout de Keycloak
    para invalidar también la sesión del Identity Provider (SSO logout).

    Flujo:
        1. Django cierra la sesión local (flush de session)
        2. Redirige al endpoint end_session de Keycloak
        3. Keycloak invalida su sesión y redirige de vuelta a la app
    """

    def get(self, request):
        # Cerrar sesión de Django
        logout(request)

        # Construir URL de logout de Keycloak
        keycloak_logout_url = getattr(
            settings,
            "OIDC_OP_LOGOUT_ENDPOINT",
            "",
        )

        if keycloak_logout_url:
            # post_logout_redirect_uri le dice a Keycloak a dónde volver
            redirect_uri = request.build_absolute_uri(
                getattr(settings, "LOGOUT_REDIRECT_URL", "/")
            )
            params = urlencode({
                "client_id": settings.OIDC_RP_CLIENT_ID,
                "post_logout_redirect_uri": redirect_uri,
            })
            full_logout_url = f"{keycloak_logout_url}?{params}"

            logger.info("Logout SSO: redirigiendo a Keycloak")
            return redirect(full_logout_url)

        # Fallback: si no hay endpoint de logout configurado
        logger.warning(
            "OIDC_OP_LOGOUT_ENDPOINT no configurado, logout solo local"
        )
        return redirect(getattr(settings, "LOGOUT_REDIRECT_URL", "/"))
