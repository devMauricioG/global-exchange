import logging
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View

logger = logging.getLogger(__name__)


def home_view(request):
    """
    Vista de bienvenida en la raíz '/' que muestra el estado de la sesión,
    datos del usuario autenticado, roles y botón de logout SSO.
    """
    if request.user.is_authenticated:
        groups = ", ".join([g.name for g in request.user.groups.all()]) or "Sin grupos asignados"
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Global Exchange - Sesión Activa</title>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
                .card {{ background: #1e293b; padding: 2.5rem; border-radius: 1rem; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 100%; max-width: 480px; border: 1px solid #334155; }}
                .badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; background: #10b981; color: #022c22; margin-bottom: 1rem; }}
                h1 {{ margin-top: 0; font-size: 1.75rem; color: #38bdf8; }}
                .info-row {{ display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #334155; font-size: 0.95rem; }}
                .info-label {{ color: #94a3b8; font-weight: 500; }}
                .info-value {{ font-weight: 600; color: #f1f5f9; }}
                .actions {{ margin-top: 2rem; display: flex; gap: 1rem; }}
                .btn {{ flex: 1; text-align: center; padding: 0.75rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600; transition: all 0.2s; }}
                .btn-admin {{ background: #3b82f6; color: white; }}
                .btn-admin:hover {{ background: #2563eb; }}
                .btn-logout {{ background: #ef4444; color: white; }}
                .btn-logout:hover {{ background: #dc2626; }}
            </style>
        </head>
        <body>
            <div class="card">
                <span class="badge">● Sesión SSO Activa</span>
                <h1>¡Bienvenido, {request.user.first_name or request.user.username}!</h1>
                <div class="info-row"><span class="info-label">Usuario:</span><span class="info-value">{request.user.username}</span></div>
                <div class="info-row"><span class="info-label">Email:</span><span class="info-value">{request.user.email}</span></div>
                <div class="info-row"><span class="info-label">Nombre Completo:</span><span class="info-value">{request.user.get_full_name() or '-'}</span></div>
                <div class="info-row"><span class="info-label">Es Staff (Admin/Operador):</span><span class="info-value">{'Sí' if request.user.is_staff else 'No'}</span></div>
                <div class="info-row"><span class="info-label">Es Superusuario:</span><span class="info-value">{'Sí' if request.user.is_superuser else 'No'}</span></div>
                <div class="info-row"><span class="info-label">Grupos asignados:</span><span class="info-value">{groups}</span></div>
                <div class="actions">
                    <a href="/customers/" class="btn btn-primary" style="background: linear-gradient(135deg, #38bdf8 0%, #2563eb 100%); color: white;">Gestión Clientes</a>
                    {'<a href="/admin/" class="btn btn-admin">Panel Admin</a>' if request.user.is_staff else ''}
                    <a href="/auth/logout/" class="btn btn-logout">Cerrar Sesión SSO</a>
                </div>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
    else:
        return redirect('/oidc/authenticate/')



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
