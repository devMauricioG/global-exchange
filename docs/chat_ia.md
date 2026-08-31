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
- Analicé los requisitos de UX del módulo `customers` y definí la arquitectura
  visual: sistema de badges por segmento, avatares con iniciales, paleta de colores
  por tipo de cliente (Minorista, Mayorista, Corporativo, VIP) y layout responsivo.
- Diseñé e implementé el listado interactivo (`cliente_list.html`): tarjetas KPI
  de estadísticas, pestañas de filtrado rápido por segmento, tabla con acciones
  por fila y estado vacío amigable. Usé el asistente de IA para validar opciones
  de estructura CSS y obtener sugerencias de componentes, que luego adapté al
  sistema de diseño del proyecto.
- Implementé el formulario de alta/edición (`cliente_form.html`) dividido en
  secciones, con selector visual de segmentación por tarjetas tipo card y toggle
  de estado. La integración con el `<select>` de Django y la validación visual
  por campo la resolví yo; la IA fue consultada puntualmente para ideas de
  presentación del toggle switch y manejo de errores.
- Rediseñé la ficha de detalle (`cliente_detail.html`) y la pantalla de
  confirmación de eliminación (`cliente_confirm_delete.html`). El diseño de la
  animación de alerta y la jerarquía visual fueron decisiones propias; recurrí
  a la IA para generar variantes de estilos CSS que luego seleccioné y ajusté.
- Verifiqué la integridad de todo el módulo con la suite de pruebas automatizadas
  (`manage.py test`) antes de publicar los cambios.

---
