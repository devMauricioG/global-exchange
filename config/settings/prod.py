import os
from .base import *

DEBUG = False

# En producción DEBES definir ALLOWED_HOSTS explícitamente en el entorno
ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]

# Seguridad en producción (HTTPS / Cookies seguras)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
