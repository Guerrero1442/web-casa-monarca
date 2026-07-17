# Casa Monarca Conecta - Master System Rules

## 1. Contexto Global y Arquitectura
- **Propósito:** Plataforma web para la gestión de voluntarios de ayuda humanitaria (Monterrey, México).
- **Objetivo Técnico:** Eliminar el sobrecupo en eventos, mantener trazabilidad de asistencia y automatizar la comunicación.
- **Vistas del Administrador:** Dashboard de métricas, formulario de creación de eventos y panel de control de asistencia (asignación de horas y disparo de correos).
- **Vistas del Voluntario:** Catálogo de eventos disponibles, detalle/inscripción, agenda de turnos inscritos, historial de horas confirmadas y gestión de perfil.

## 2. Lógica de Negocio Crítica
- **Validación Atómica de Cupos:** Obligatorio utilizar transacciones con bloqueo de fila (`SELECT ... FOR UPDATE`) en el backend para evitar condiciones de carrera durante la inscripción.
- **Registro de Horas:** El contador de impacto del voluntario suma exclusivamente la duración de los eventos donde el administrador marcó el estado `asistio = True`.
- **Restricción OAuth:** Si el usuario se autentica vía Google/Facebook y el campo `telefono` es nulo, el sistema debe bloquear cualquier intento de inscripción y redirigir a la vista de perfil para su captura obligatoria.

## 3. Cumplimiento Normativo (LFPDPPP México)
- **Derechos ARCO:** Estrictamente prohibido ejecutar sentencias `DELETE` físicas sobre la tabla de `usuarios`. 
- **Anonimización:** Las solicitudes de baja deben procesarse sobrescribiendo los datos personales (nombre, correo, teléfono) con valores genéricos, manteniendo intacta la relación de llaves foráneas en `inscripciones` para conservar la integridad estadística.

## 4. Stack Tecnológico
- **Backend:** FastAPI (Python), SQLAlchemy, Alembic. Base de datos: PostgreSQL (Supabase).
- **Frontend:** Tailwind CSS.
- **Procesamiento Asíncrono:** Uso de `fastapi.BackgroundTasks` para integración de Resend API (correos).

## 5. Protocolo de Ejecución de Skills (Rutas de Contexto)
El agente DEBE referenciar estos manuales antes y durante la generación de código:
1. **Arranque y Estructura:** Ejecutar 👉 `/.agent/skills/inicializar_proyecto.md`
2. **Base de Datos y Migraciones:** Consultar 👉 `/.agent/skills/gestionar_migracion_supabase.md`
3. **Autenticación (JWT/OAuth):** Consultar 👉 `/.agent/skills/auditar_flujo_oauth.md`
4. **UI/UX y Tokens Base:** Aplicar estrictamente 👉 `/.agent/context/design/theme_specs.md`

## 6. Reglas Operativas y Restricciones Estrictas
- **Flujo de Trabajo:** Ejecutar la inicialización del proyecto antes de escribir lógica de negocio. Generar planes de implementación estructurados para flujos complejos.
- **Seguridad:** Toda ruta conectada a la base de datos exige validación de JWT y verificación de control de acceso basado en roles (RBAC).
- **Calidad de Código:** Utilizar `Ruff` (linting) y `Pyright` (tipado estricto). Todos los modelos de SQLAlchemy deben tener su esquema Pydantic correspondiente.
- **Prohibición de Destrucción:** NO ejecutar comandos destructivos en la terminal (`rm`, `drop`) sin solicitar confirmación con el prefijo: 'WARNING: POTENTIALLY DESTRUCTIVE ACTION REQUIRED'.
- **Restricciones de Frontend (Tailwind):** Prohibido utilizar colores hexadecimales arbitrarios en las clases (ej. `text-[#C36B53]`). Usar obligatoriamente las variables del tema (`Primary`: #C36B53, `Secondary`: #23352F, `Background`: #F5F3ED, `Surface`: #FFFFFF). Reutilizar componentes consolidados (`btn-primary`, `card-evento`) vía `@apply`.