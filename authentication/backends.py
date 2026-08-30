"""
Backend de autenticación OIDC personalizado para Keycloak.

Extiende OIDCAuthenticationBackend de mozilla-django-oidc para:
- Crear usuarios automáticamente a partir de claims OIDC
- Actualizar datos del usuario en cada login
- Mapear roles de Keycloak a grupos y permisos de Django
"""

import logging

from django.contrib.auth.models import Group
from mozilla_django_oidc.auth import OIDCAuthenticationBackend

logger = logging.getLogger(__name__)


class KeycloakOIDCAuthenticationBackend(OIDCAuthenticationBackend):
    """
    Backend OIDC que integra Keycloak con el sistema de usuarios de Django.

    Claims esperadas del token ID de Keycloak:
        - email: correo electrónico del usuario
        - preferred_username: nombre de usuario
        - given_name: nombre
        - family_name: apellido
        - realm_roles: lista de roles del realm (requiere protocol mapper)
    """

    def create_user(self, claims):
        """
        Crea un nuevo usuario de Django a partir de las claims OIDC.

        Se invoca automáticamente cuando un usuario inicia sesión por primera
        vez vía Keycloak y no existe en la base de datos local de Django.
        """
        user = super().create_user(claims)
        self._update_user_from_claims(user, claims)
        logger.info("Usuario creado vía OIDC: %s", user.username)
        return user

    def update_user(self, user, claims):
        """
        Actualiza un usuario existente con claims frescas en cada login.

        Garantiza que los datos locales de Django (nombre, email, roles)
        estén siempre sincronizados con Keycloak.
        """
        self._update_user_from_claims(user, claims)
        logger.info("Usuario actualizado vía OIDC: %s", user.username)
        return user

    def filter_users_by_claims(self, claims):
        """
        Busca usuarios existentes por email para evitar duplicados.

        Keycloak garantiza unicidad del email, así que usamos este campo
        como identificador principal para vincular cuentas.
        """
        email = claims.get("email")
        if not email:
            return self.UserModel.objects.none()
        return self.UserModel.objects.filter(email=email)

    def _update_user_from_claims(self, user, claims):
        """
        Actualiza los campos del usuario y sus grupos/permisos
        a partir de las claims del token OIDC.
        """
        user.email = claims.get("email", user.email)
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")
        user.username = claims.get("preferred_username", user.username)

        # Mapear roles de Keycloak a permisos de Django
        realm_roles = claims.get("realm_roles", [])
        self._map_roles_to_permissions(user, realm_roles)

        user.save()

    def _map_roles_to_permissions(self, user, realm_roles):
        """
        Mapea roles del realm de Keycloak a grupos y permisos de Django.

        Mapeo:
            - 'admin'    → is_staff=True, is_superuser=True, grupo 'admin'
            - 'operator' → is_staff=True, is_superuser=False, grupo 'operator'
            - 'user'     → is_staff=False, is_superuser=False, grupo 'user'
        """
        # Reset de permisos base antes de recalcular
        user.is_staff = False
        user.is_superuser = False

        # Limpiar grupos anteriores para resincronizar
        user.groups.clear()

        for role in realm_roles:
            role_lower = role.lower()

            if role_lower == "admin":
                user.is_staff = True
                user.is_superuser = True

            elif role_lower == "operator":
                user.is_staff = True

            # Crear el grupo si no existe y asignar al usuario
            if role_lower in ("admin", "operator", "user"):
                group, _ = Group.objects.get_or_create(name=role_lower)
                user.groups.add(group)

        logger.debug(
            "Roles mapeados para %s: roles=%s, is_staff=%s, is_superuser=%s",
            user.username,
            realm_roles,
            user.is_staff,
            user.is_superuser,
        )
