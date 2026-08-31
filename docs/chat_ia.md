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

## Pablo Elizeche — 31/08/2026 — Antigravity IDE (Google DeepMind)

**Contexto:** Sprint 1 — Construcción de interfaces gráficas para clientes (SCRUM-29)

**Resumen:**
- Análisis de la estructura visual existente (`base.html`, tokens CSS del sistema de diseño)
  para identificar las brechas de UX en las plantillas del módulo `customers`.
- Diseño de la arquitectura de componentes CSS: paleta segmentada por tipo de cliente
  (Minorista, Mayorista, Corporativo, VIP), sistema de badges semánticos, avatares
  dinámicos con iniciales y gradientes de color por segmento.
- Estructuración del layout de `cliente_list.html`: tarjetas KPI de estadísticas,
  pestañas de filtrado rápido por segmento, barra de filtros avanzada y tabla interactiva
  con acciones por fila. La IA fue utilizada como herramienta de asistencia en la
  generación de la maqueta base; el ajuste de estilos, la integración con las vistas
  Django y la revisión de accesibilidad fueron realizados manualmente.
- Maquetación del formulario (`cliente_form.html`) con selector visual de segmentación
  por tarjetas tipo card (en lugar del `<select>` estándar), toggle de estado y
  secciones agrupadas con cabeceras descriptivas.
- Rediseño de `cliente_detail.html` con perfil hero, avatar grande con iniciales,
  tarjetas de datos con iconos y barra de timestamps.
- Mejora de `cliente_confirm_delete.html` con ícono animado de advertencia y resumen
  del cliente a eliminar para confirmar la acción crítica.
- Verificación con la suite de pruebas automatizadas (`manage.py test`) tras cada
  cambio para asegurar la integridad de las vistas.

---