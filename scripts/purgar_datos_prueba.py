import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from src.database import SessionLocal


def purgar_datos_prueba():
    db = SessionLocal()
    try:
        print("[Purgado de Datos] Iniciando borrado en cascada de datos de prueba...")
        db.execute(text("DELETE FROM reservas;"))
        db.execute(text("DELETE FROM solicitudes;"))
        db.execute(text("DELETE FROM eventos;"))
        db.execute(text("DELETE FROM menores;"))
        db.commit()
        print("[Purgado de Datos] OK: Tablas 'reservas', 'solicitudes', 'eventos' y 'menores' limpiadas exitosamente.")
        print("[Purgado de Datos] OK: Registros de la tabla 'usuarios' preservados intactos.")
    except Exception as e:
        db.rollback()
        print(f"[Purgado de Datos] ERROR: Error al purgar la base de datos: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    purgar_datos_prueba()
