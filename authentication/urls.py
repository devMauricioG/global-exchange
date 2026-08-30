"""
URL patterns para la app de autenticación.

Rutas:
    /auth/logout/  → Logout unificado SSO (Django + Keycloak)
"""

from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path("logout/", views.KeycloakLogoutView.as_view(), name="logout"),
]
