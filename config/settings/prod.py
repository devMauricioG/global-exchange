"""
Configuración de producción para Global Exchange.

Este módulo extiende la configuración base y aplica prácticas recomendadas de seguridad,
persistencia y conectividad para entornos de producción.
"""

import os
from .base import *

# Modo producción
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

# Hosts permitidos (obligatorio en producción)
ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1,web').split(',')
    if host.strip()
]

# Configuración de Base de Datos (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'global_exchange_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.getenv('DB_CONN_MAX_AGE', 600)),
    }
}

# ─── Integración OIDC / Keycloak para Producción ──────────────────────────────
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://keycloak:8080")
KEYCLOAK_PUBLIC_URL = os.getenv("KEYCLOAK_PUBLIC_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "GlobalExchangeRealm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "django-app")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

# Endpoints públicos (el navegador del cliente es redirigido a estos)
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    f"{KEYCLOAK_PUBLIC_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
)
OIDC_OP_LOGOUT_ENDPOINT = (
    f"{KEYCLOAK_PUBLIC_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
)

# Endpoints internos (Django se comunica directamente servidor a servidor)
OIDC_OP_TOKEN_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
)
OIDC_OP_USER_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
)
OIDC_OP_JWKS_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
)

# Credenciales de Relying Party
OIDC_RP_CLIENT_ID = KEYCLOAK_CLIENT_ID
OIDC_RP_CLIENT_SECRET = KEYCLOAK_CLIENT_SECRET
OIDC_RP_SIGN_ALGO = os.getenv("OIDC_RP_SIGN_ALGO", "RS256")
OIDC_RP_SCOPES = "openid email profile"
OIDC_CREATE_USER = True
OIDC_VERIFY_SSL = os.getenv("OIDC_VERIFY_SSL", "False").lower() in ("true", "1")

# ─── Configuración de Correo Electrónico ─────────────────────────────────────
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'mailpit')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() in ('true', '1')
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() in ('true', '1')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@globalexchange.local')

# ─── Configuración de Seguridad y Proxy Inverso ──────────────────────────────
# Headers de proxy si se usa Nginx o Traefik
if os.getenv('USE_HTTPS', 'False').lower() in ('true', '1'):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Orígenes confiables para CSRF
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
if csrf_origins:
    CSRF_TRUSTED_ORIGINS = [orig.strip() for orig in csrf_origins.split(',') if orig.strip()]
else:
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

# Archivos estáticos
STATIC_ROOT = BASE_DIR / 'staticfiles'
