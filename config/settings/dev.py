import os
from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Conexión a PostgreSQL (compatible con Docker y local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'global_exchange_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Integración Keycloak
KEYCLOAK_SERVER_URL = os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "GlobalExchangeRealm")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "django-app")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "tu-secret-local")

# Configuración de Servidor SMTP (Mailpit en desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', '127.0.0.1')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 1025))
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'noreply@globalexchange.local'

# ─── Configuración OIDC (mozilla-django-oidc + Keycloak) ───────────────────────

# Endpoints del OpenID Provider (Keycloak)
OIDC_OP_AUTHORIZATION_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth"
)
OIDC_OP_TOKEN_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
)
OIDC_OP_USER_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
)
OIDC_OP_JWKS_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
)
OIDC_OP_LOGOUT_ENDPOINT = (
    f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout"
)

# Credenciales del Relying Party (cliente django-app en Keycloak)
OIDC_RP_CLIENT_ID = KEYCLOAK_CLIENT_ID
OIDC_RP_CLIENT_SECRET = KEYCLOAK_CLIENT_SECRET

# Algoritmo de firma de tokens (RS256 = clave asimétrica vía JWKS)
OIDC_RP_SIGN_ALGO = os.getenv("OIDC_RP_SIGN_ALGO", "RS256")

# Scopes solicitados al proveedor OIDC
OIDC_RP_SCOPES = "openid email profile"

# Permitir crear usuarios automáticamente en el primer login OIDC
OIDC_CREATE_USER = True

# No verificar SSL en desarrollo (Keycloak corre en HTTP)
OIDC_VERIFY_SSL = not DEBUG
