from datetime import timedelta
from sqlalchemy.orm import Session
from loguru import logger
from src.solicitudes.models import Solicitud
from src.eventos.models import Evento, Reserva


def recalcular_estado_solicitud(db: Session, solicitud: Solicitud) -> str:
    """Calcula con precisión matemática y aritmética el estado de cobertura de una solicitud.

    - 'Cubierta': Las reservas confirmadas cubren el 100% de la duración solicitada (duracion_reservada >= duracion_solicitada).
    - 'Parcial': Existe al menos una reserva confirmada pero la cobertura de tiempo es incompleta (0 < duracion_reservada < duracion_solicitada).
    - 'Pendiente': No existe ninguna reserva ejecutada o confirmada (duracion_reservada == 0).
    """
    logger.info(
        f"[Recálculo Estado] Evaluando solicitud ID {solicitud.id} | "
        f"Inicio Requerido: {solicitud.inicio_requerido} | Fin Requerido: {solicitud.fin_requerido}"
    )

    duracion_solicitada = solicitud.fin_requerido - solicitud.inicio_requerido
    if duracion_solicitada <= timedelta(0):
        return "Pendiente"

    # Obtener las reservas confirmadas asociadas a esta solicitud
    reservas = db.query(Reserva).filter(Reserva.solicitud_id == solicitud.id).all()

    duracion_reservada = timedelta(0)
    for res in reservas:
        evento = db.query(Evento).filter(Evento.id == res.evento_id).first()
        if evento:
            # Cobertura de límites inclusivos (<= y >=)
            inicio_efectivo = max(solicitud.inicio_requerido, evento.inicio_evento)
            fin_efectivo = min(solicitud.fin_requerido, evento.fin_evento)
            if fin_efectivo > inicio_efectivo:
                duracion_reservada += (fin_efectivo - inicio_efectivo)

    logger.info(
        f"[Recálculo Estado] Solicitud {solicitud.id} -> "
        f"Duración Solicitada: {duracion_solicitada} | Duración Reservada: {duracion_reservada}"
    )

    if duracion_reservada >= duracion_solicitada:
        return "Cubierta"
    elif duracion_reservada > timedelta(0):
        return "Parcial"
    else:
        return "Pendiente"


def recalcular_todas_las_solicitudes(db: Session) -> None:
    """Recalcula y actualiza atómicamente el estado de todas las solicitudes."""
    solicitudes = db.query(Solicitud).all()
    for sol in solicitudes:
        nuevo_estado = recalcular_estado_solicitud(db, sol)
        if sol.estado != nuevo_estado:
            sol.estado = nuevo_estado
            db.add(sol)
    db.commit()
