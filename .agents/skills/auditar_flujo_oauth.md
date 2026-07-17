# Descripción
Valida la extracción robusta del payload JWT proveniente de Supabase y su respectivo mapeo hacia Pydantic y SQLAlchemy.

# Instrucciones de Ejecución
Al generar o refactorizar el módulo de autorización:
1. Validar que la llave secreta (`SUPABASE_JWT_SECRET`) se inyecte estrictamente mediante `pydantic-settings` y nunca mediante lectura cruda de `os.environ`.
2. Inspeccionar la función decodificadora. Exigir la validación del objeto `user_metadata` y la inyección de valores por defecto si atributos como el teléfono vienen vacíos desde el proveedor (Google/Facebook).
3. Asegurar que las excepciones lanzadas por firmas inválidas o caducadas hereden de `HTTPException` y posean el código de estado 401.