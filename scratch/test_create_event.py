import uuid
from datetime import datetime, timedelta
from src.database import SessionLocal
from src.eventos.models import Evento
from src.usuarios.models import Usuario

def test_insert():
    db = SessionLocal()
    try:
        # 1. Crear un usuario admin ficticio para verificar claves foráneas
        admin_id = uuid.uuid4()
        admin = Usuario(
            id=admin_id,
            nombre="Admin Test",
            correo="admin_scratch@test.com",
            rol="admin",
            proveedor_auth="email",
            activo=True
        )
        db.add(admin)
        db.commit()
        print(f"Usuario admin insertado con ID: {admin_id}")

        # 2. Crear evento
        evento = Evento(
            id=uuid.uuid4(),
            titulo="Evento de Prueba Scratch",
            descripcion="Descripción de prueba",
            fecha_inicio=datetime.utcnow(),
            fecha_fin=datetime.utcnow() + timedelta(hours=2),
            duracion_horas=2.0,
            cupo_maximo=10,
            lugar="Oficinas Casa Monarca",
            id_admin=admin_id
        )
        db.add(evento)
        db.commit()
        print("Evento insertado con éxito en PostgreSQL local")

        # Limpiar
        db.delete(evento)
        db.delete(admin)
        db.commit()
        print("Limpieza completada")
    except Exception as e:
        db.rollback()
        print(f"ERROR DETECTADO: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    test_insert()
