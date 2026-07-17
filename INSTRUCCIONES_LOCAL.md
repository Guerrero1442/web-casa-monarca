# Guía de Ejecución Local - Casa Monarca Conecta

Sigue estos pasos para levantar el entorno de desarrollo local (tanto el Backend como el Frontend) en tu PC.

---

## 🛠 Requisitos Previos

1. **Python 3.12+** instalado.
2. **Node.js 18+** y `npm` instalados.
3. El administrador de paquetes/entornos de Python **uv** (para ejecutar scripts del backend de forma rápida y aislada). Si no lo tienes, puedes instalarlo ejecutando:
   ```bash
   pip install uv
   ```

---

## 1. Configuración del Backend (FastAPI)

1. En la raíz del repositorio, copia el archivo de entorno de ejemplo:
   ```bash
   copy .env.example .env
   ```
2. Abre el archivo `.env` recién creado y completa las credenciales:
   * **`DATABASE_URL`**: URL de conexión a tu base de datos PostgreSQL (puede ser local o la base de datos Supabase provista).
   * **`SUPABASE_JWT_SECRET`**: Secreto JWT de tu proyecto Supabase (necesario para verificar la autenticidad de los tokens enviados por los voluntarios).
3. Levanta las tablas y aplica las migraciones de Alembic:
   ```bash
   uv run alembic upgrade head
   ```
4. Inicia el servidor de desarrollo de FastAPI:
   ```bash
   uv run uvicorn src.main:app --reload --port 8000
   ```
   El backend estará escuchando en **`http://localhost:8000`**.

---

## 2. Configuración del Frontend (Astro)

1. Entra al directorio `frontend/`:
   * En tu terminal o consola: `cd frontend`
2. Copia el archivo de entorno de ejemplo:
   ```bash
   copy .env.example .env
   ```
3. Abre el archivo `frontend/.env` y completa las variables públicas:
   * **`PUBLIC_API_URL`**: Por defecto `http://localhost:8000` (FastAPI).
   * **`PUBLIC_SUPABASE_URL`**: URL del endpoint de tu proyecto Supabase.
   * **`PUBLIC_SUPABASE_ANON_KEY`**: Clave pública anónima de Supabase.
4. Instala las dependencias de node:
   ```bash
   npm install
   ```
5. Inicia el servidor de desarrollo de Astro:
   ```bash
   npm run dev
   ```
   Astro levantará el servidor del cliente, usualmente en **`http://localhost:4321`**.

---

## 3. Pruebas Rápidas en Desarrollo (Bypass de OAuth)

* **Voluntariado Directo**: Si no tienes configurado Supabase aún o deseas probar la navegación local sin redirección real de OAuth, puedes pulsar el botón **"Entrar como Voluntario"** en la Landing (`http://localhost:4321`). Este botón te redirigirá directamente al catálogo y desactivará el inicio de sesión OAuth para pruebas ágiles en local.
* **Control de Asistencia (Admin)**: Puedes cambiar manualmente los roles de los usuarios registrados en tu base de datos a `"admin"` para ingresar a la ruta `/admin/dashboard` y probar el flujo de confirmación masiva.
