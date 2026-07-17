# Descripción
Instrucciones detalladas para inicializar el entorno virtual, las dependencias y la estructura base del proyecto desde cero.

# Pasos de Ejecución Obligatorios

## Paso 1: Configuración del Entorno y Dependencias
1. Ejecutar el comando para inicializar el proyecto con el gestor de paquetes avanzado: `uv init --app`.
2. Reemplazar o actualizar el archivo `pyproject.toml` para incluir las siguientes dependencias estrictas:
   - fastapi
   - uvicorn[standard]
   - sqlalchemy
   - alembic
   - psycopg2-binary
   - pydantic-settings
   - python-jose[cryptography]
   - loguru
   - ruff
   - pyright
3. Sincronizar el entorno de desarrollo ejecutando: `uv sync`.

## Paso 2: Generación de la Estructura de Archivos
1. Crear el árbol de directorios dentro de la carpeta `src/` conforme a la arquitectura modular establecida.
2. Inicializar los archivos `__init__.py` en cada submódulo para asegurar la correcta resolución de importaciones.

## Paso 3: Configuración de Base de Datos y Modelos Base
1. En `src/database.py`, configurar el motor de SQLAlchemy y el `SessionLocal` manejando de forma dinámica la variable `DATABASE_URL`.
2. Definir en cada archivo `models.py` la estructura relacional especificada.

## Paso 4: Inicialización de Migraciones con Alembic
1. Ejecutar `uv run alembic init alembic` en la raíz del proyecto.
2. Modificar el archivo `alembic/env.py` para importar el objeto `Base` de los modelos y asignar `target_metadata = Base.metadata`.
3. Configurar `alembic.ini` para que herede la cadena de conexión desde las variables de entorno.
4. Generar la migración inicial: `uv run alembic revision --autogenerate -m "init_db"`.