# Especificaciones de Diseño y UI (Casa Monarca - Cuidado Infantil)

## 1. Sistema de Diseño Base
*   **Framework CSS:** Tailwind CSS.
*   **Paleta de Colores:** Mantener un esquema de alto contraste y legibilidad. Tonos neutros para fondos y colores semánticos para los estados de las solicitudes.
*   **Tipografía:** Sans-serif estándar (Inter o Roboto), priorizando la legibilidad y la responsividad en dispositivos móviles, dado que es el dispositivo principal de acceso para las madres.

## 2. Vistas de Usuario: Madre

### 2.1. Formulario de Solicitud (`frontend/src/pages/solicitud.astro`)
*   **Datos del Menor:** 
    *   Campos de texto para `nombre`.
    *   Selector de fecha (tipo `date`) para `fecha_nacimiento` (el sistema debe calcular la edad en la vista).
    *   Áreas de texto (Textarea) obligatorias o con opción "Ninguna" para `alergias` y `requerimientos_medicos`.
*   **Rango Horario:** 
    *   Selectores de tipo `time` para `hora_inicio` y `hora_fin`.
    *   Selector de tipo `date` para `fecha_requerida`.
*   **Validación de Interfaz:** Prevenir el envío del formulario mediante validación en el cliente si `hora_inicio` es mayor o igual a `hora_fin`.

### 2.2. Panel Principal (Dashboard Madres)
*   **Estado de Solicitudes:** Tarjetas (Cards) indicando el estado actual de cada solicitud enviada (Pendiente, Parcial, Cubierta).
*   **Eventos Recomendados:** Sección dinámica que lista los eventos generados por el administrador que intersectan temporalmente con las franjas horarias solicitadas.
*   **Acciones:** Botón de confirmación (reserva) habilitado únicamente si el evento sugerido cuenta con aforo disponible.

## 3. Vistas de Usuario: Administrador

### 3.1. Consolidado de Solicitudes (`frontend/src/pages/admin/dashboard.astro`)
*   **Visualización:** Tabla de datos o vista de línea de tiempo (Timeline) que agrupe las solicitudes por `fecha_requerida` y franja horaria.
*   **Métricas Operativas:** Indicadores de demanda (conteo de menores por hora/día) para facilitar la creación eficiente de eventos.

### 3.2. Creación de Eventos
*   **Formulario:** Campos obligatorios para `fecha`, `hora_inicio`, `hora_fin` y `capacidad_maxima` (input numérico).
*   **Interacción Asíncrona:** Al ejecutar la creación del evento, el botón de submit debe deshabilitarse y mostrar un indicador de carga (spinner), reflejando el procesamiento asíncrono (despacho de notificaciones) en el backend sin bloquear la interfaz.

## 4. Componentes Reutilizables (UI Kit)

*   **CardEvento (`frontend/src/components/CardEvento.astro`):** Componente para renderizar los detalles del evento (horario, aforo disponible/máximo). Debe incluir renderizado condicional de etiquetas visuales que indiquen si la cobertura horaria es "Total" o "Parcial" respecto a la solicitud original de la madre.
*   **BadgeEstado:** Componente de etiqueta de color estandarizada para los estados de la solicitud:
    *   Pendiente: Tonos amarillos/ámbar.
    *   Parcial: Tonos naranjas.
    *   Cubierta: Tonos verdes.
*   **ToastNotificacion:** Sistema de alertas efímeras (no bloqueantes) para confirmar la creación de eventos, el éxito de una reserva o los errores de validación.