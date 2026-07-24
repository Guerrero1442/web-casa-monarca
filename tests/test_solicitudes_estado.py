import unittest
from datetime import datetime, timezone
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.usuarios.models import Usuario  # noqa: F401
from src.menores.models import Menor    # noqa: F401
from src.solicitudes.models import Solicitud
from src.eventos.models import Evento
from src.solicitudes.service import recalcular_estado_solicitud, recalcular_todas_las_solicitudes


class TestSolicitudesEstado(unittest.TestCase):
    def test_recalculo_estado_sin_eventos(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine)
        db = Session()

        madre_id = uuid.uuid4()
        menor_id = uuid.uuid4()

        # Solicitud para el 25/07/2026 de 09:00 a 13:00 UTC
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

        # Al no existir eventos en BD, el estado recalculado debe ser 'Pendiente'
        estado = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado, "Pendiente")

        # Publicar un evento para el 26/07/2026 (otro día, no intersecta)
        evento_otro_dia = Evento(
            id=uuid.uuid4(),
            titulo="Evento Otro Día",
            inicio_evento=datetime(2026, 7, 26, 9, 0, tzinfo=timezone.utc),
            fin_evento=datetime(2026, 7, 26, 13, 0, tzinfo=timezone.utc),
            capacidad_maxima=10,
            id_admin=uuid.uuid4(),
        )
        db.add(evento_otro_dia)
        db.commit()

        # Debe seguir en estado 'Pendiente' porque el evento es en otra fecha
        estado_despues = recalcular_estado_solicitud(db, solicitud)
        self.assertEqual(estado_despues, "Pendiente")

        # Publicar un evento que SÍ intersecta el 25/07/2026 (10:00 a 12:00)
        evento_intersecta = Evento(
            id=uuid.uuid4(),
            titulo="Evento Intersecta",
            inicio_evento=datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc),
            fin_evento=datetime(2026, 7, 25, 12, 0, tzinfo=timezone.utc),
            capacidad_maxima=10,
            id_admin=uuid.uuid4(),
        )
        db.add(evento_intersecta)
        db.commit()

        # Al haber un evento intersectado, el estado cambia a 'Parcial'
        recalcular_todas_las_solicitudes(db)
        db.refresh(solicitud)
        self.assertEqual(solicitud.estado, "Parcial")


if __name__ == "__main__":
    unittest.main()
