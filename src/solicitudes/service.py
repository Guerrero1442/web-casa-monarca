from sqlalchemy.orm import Session
from loguru import logger
from src.solicitudes.models import Solicitud
from src.eventos.models import Evento, Reserva


def recalcular_estado_solicitud(db: Session, solicitud: Solicitud) -> str:
    """Calcula con precisión matemática el estado de cobertura de una solicitud.

    - 'Pendiente': 0 eventos de cuidado coinciden en la franja fecha/hora (déficit 100%).
    - 'Cubierta': Existe reserva confirmada y el evento cubre la totalidad de la franja.
    - 'Parcial': Existen eventos que intersectan temporalmente pero la cobertura es parcial o no reservada.
    """
    logger.info(
        f"[Recálculo Estado] Evaluando solicitud ID {solicitud.id} | "
        f"Inicio Requerido: {solicitud.inicio_requerido} | Fin Requerido: {solicitud.fin_requerido}"
    )

    # 1. Comprobar si existe reserva activa confirmada para esta solicitud
    reserva = db.query(Reserva).filter(Reserva.solicitud_id == solicitud.id).first()
    if reserva:
        evento = db.query(Evento).filter(Evento.id == reserva.evento_id).first()
        if evento:
            if evento.inicio_evento <= solicitud.inicio_requerido and evento.fin_evento >= solicitud.fin_requerido:
                return "Cubierta"
            return "Parcial"

    # 2. Evaluación de intersección temporal en BD (Fecha + Hora unificadas en DateTime)
    # Condición de intersección estricta: Solicitud.inicio_requerido < Evento.fin_evento AND Solicitud.fin_requerido > Evento.inicio_evento
    eventos_intersectados = (
        db.query(Evento)
        .filter(
            Evento.inicio_evento < solicitud.fin_requerido,
            Evento.fin_evento > solicitud.inicio_requerido,
        )
        .all()
    )

    if not eventos_intersectados:
        logger.info(f"[Recálculo Estado] Solicitud {solicitud.id} tiene 0 eventos intersectados -> Estado: Pendiente")
        return "Pendiente"

    logger.info(f"[Recálculo Estado] Solicitud {solicitud.id} intersecta con {len(eventos_intersectados)} evento(s) -> Estado: Parcial")
    return "Parcial"


def recalcular_todas_las_solicitudes(db: Session) -> None:
    """Recalcula y actualiza atómicamente el estado de todas las solicitudes."""
    solicitudes = db.query(Solicitud).all()
    for sol in solicitudes:
        nuevo_estado = recalcular_estado_solicitud(db, sol)
        if sol.estado != nuevo_estado:
            sol.estado = nuevo_estado
            db.add(sol)
    db.commit()
