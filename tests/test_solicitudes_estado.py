import unittest
from datetime import datetime, timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.usuarios.models import Usuario  # noqa: F401
from src.menores.models import Menor    # noqa: F401
from src.solicitudes.models import Solicitud
from src.eventos.models import Evento, Reserva
from src.solicitudes.service import recalcular_estado_solicitud, recalcular_todas_las_solicitudes


class TestSolicitudesEstado(unittest.TestCase):
    def test_recalculo_estado_aritmético(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        madre_id = uuid.uuid4()
        menor_id = uuid.uuid4()

        # Solicitud para el 25/07/2026 de 09:00 a 13:00 UTC (4 horas)
        solicitud = Solicitud(
            id=uuid.uuid4(),
            madre_id=madre_id,
            menor_id=menor_id,
            inicio_requerido=datetime(2026, 7, 25, 9, 0, tzinfo=timezone.utc),
            fin_requerido=datetime(2026, 7, 25, 13, 0, tzinfo=timezone.utc),
            estado="Pendiente",
        )
        db.add(solicitud)
        db.commit()

        # 1. Sin reservas ejecutadas -> Debe ser estrictamente 'Pendiente'
        estado_inicial = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_inicial, "Pendiente")

        # Crear un evento idéntico en horario (09:00 a 13:00)
        evento_identico = Evento(
            id=uuid.uuid4(),
            titulo="Evento Completo",
            inicio_evento=datetime(2026, 7, 25, 9, 0, tzinfo=timezone.utc),
            fin_evento=datetime(2026, 7, 25, 13, 0, tzinfo=timezone.utc),
            capacidad_maxima=10,
            id_admin=uuid.uuid4(),
        )
        db.add(evento_identico)
        db.commit()

        # Sin reserva aún -> Sigue en 'Pendiente'
        estado_sin_reserva = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_sin_reserva, "Pendiente")

        # 2. Reservar cupo para el evento idéntico -> Debe pasar a 'Cubierta' (100% cobertura)
        reserva = Reserva(
            id=uuid.uuid4(),
            evento_id=evento_identico.id,
            solicitud_id=solicitud.id,
        )
        db.add(reserva)
        db.commit()

        estado_cubierta = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_cubierta, "Cubierta")

        # 3. Eliminar reserva -> Debe volver a 'Pendiente'
        db.delete(reserva)
        db.commit()

        estado_revertido = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_revertido, "Pendiente")

        # 4. Crear reserva parcial (09:00 a 11:00) -> Debe pasar a 'Parcial'
        evento_parcial = Evento(
            id=uuid.uuid4(),
            titulo="Evento Parcial",
            inicio_evento=datetime(2026, 7, 25, 9, 0, tzinfo=timezone.utc),
            fin_evento=datetime(2026, 7, 25, 11, 0, tzinfo=timezone.utc),
            capacidad_maxima=10,
            id_admin=uuid.uuid4(),
        )
        db.add(evento_parcial)
        reserva_parcial = Reserva(
            id=uuid.uuid4(),
            evento_id=evento_parcial.id,
            solicitud_id=solicitud.id,
        )
        db.add(reserva_parcial)
        db.commit()

        estado_parcial = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_parcial, "Parcial")


if __name__ == "__main__":
    unittest.main()
