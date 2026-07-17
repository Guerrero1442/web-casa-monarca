# Descripción
Instruye al agente en el proceso correcto para generar y auditar migraciones de SQLAlchemy hacia PostgreSQL.

# Instrucciones de Ejecución
Ante cualquier cambio requerido en las tablas relacionales:
1. Inspeccionar los modelos declarativos de SQLAlchemy en el proyecto.
2. Ejecutar el comando a través del gestor: `uv run alembic revision --autogenerate -m "motivo_del_cambio"`.
3. Analizar el archivo de migración resultante. Detener la ejecución si se detectan operaciones de eliminación de columnas o tablas (`op.drop_column`, `op.drop_table`) y solicitar confirmación humana.
4. Antes de aplicar los cambios en el entorno de desarrollo, generar el volcado SQL usando `uv run alembic upgrade head --sql` para revisión de integridad.