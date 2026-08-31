# Bitácora de conversaciones con IA — Global Exchange

Este documento registra las consultas realizadas a asistentes de IA durante
el desarrollo del proyecto, según lo requerido por el punto CHIA de la
consigna. Cada integrante agrega su propia entrada al usar una IA.

---

## Felipe Rivas — 30/08/2026 — Claude

**Contexto:** Sprint 1 — Setup del entorno de desarrollo (SCRUM-25, SCRUM-31)

**Resumen:**
- Debugging del entorno Docker: conflicto de puerto 5432 entre Postgres
  dockerizado y dos instancias nativas de Postgres en Windows (postgresql-x64-17
  y postgresql-x64-18) que impedían la conexión de Django a la base de datos.
- Corrección de line endings (CRLF → LF) en `docker/postgres/init-databases.sh`,
  que rompía la inicialización de Postgres al clonar el repo en Windows.
  Se agregó `.gitattributes` para prevenir el problema a futuro en todo el equipo.
- Diseño e implementación del modelo `Cliente` (SCRUM-25) en la app `customers`,
  con `TextChoices` para la segmentación (Minorista, Mayorista, Corporativo, VIP),
  verificado con pruebas manuales en el shell de Django.
- Configuración de Sphinx para documentación automática de código (SCRUM-31):
  instalación, `sphinx-quickstart`, `sphinx-apidoc` sobre la app `customers`,
  y build de HTML navegable a partir de docstrings.
- Definición del flujo de trabajo del equipo con Git Flow (ramas, tags de
  release) y planificación general del Sprint 1 según los puntos de
  evaluación de la cátedra (IDE, SCC, PUN, PDO, AMB, PLA, QA, CHIA).

---

## Pablo Elizeche — 31/08/2026 — Antigravity / Gemini

**Contexto:** Sprint 1 — Vinculación automática de identidades Keycloak con Clientes Django (SCRUM-26) y diagnóstico de entorno local

**Resumen:**
- Diagnóstico y resolución de conflicto de conexión con PostgreSQL en Windows: consulta sobre el comportamiento del mapeo de puertos en Docker Compose al colisionar con el servicio local `postgresql-x64-17` en el puerto 5432, implementando la solución de mapeo al puerto 5433 en `.env`.
- Consulta sobre patrones de diseño en Django para intercepción desacoplada de eventos de autenticación: análisis comparativo entre Middleware vs. Signals (`user_logged_in` y señales personalizadas de aplicación).
- Revisión de la estructura de claims OIDC en `mozilla-django-oidc`: validación de la extracción del claim inmutable `sub` (subject UUID) y claims de perfil (`email`, `given_name`, `family_name`).
- Asistencia en la elaboración de la suite de pruebas unitarias para cubrir casos borde en la vinculación de clientes: sincronización por `sub`, vinculación por `correo` para registros preexistentes, creación automática y tolerancia a fallos.

---