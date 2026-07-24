import uuid
from typing import List
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from loguru import logger

from src.eventos.models import Evento, Reserva
from src.eventos.schemas import EventoCreate, EventoResponse
from src.solicitudes.models import Solicitud
from src.solicitudes.service import recalcular_todas_las_solicitudes, recalcular_estado_solicitud
from src.notificaciones.service import (
    enviar_correo_solicitud_actualizada,
    enviar_correo_reserva_confirmada,
)


def crear_evento(
    db: Session,
    evento_in: EventoCreate,
    admin_id: uuid.UUID,
    background_tasks: BackgroundTasks,
) -> Evento:
    logger.info(
        f"[Service Crear Evento] Payload - inicio_evento: {evento_in.inicio_evento!r}, fin_evento: {evento_in.fin_evento!r}"
    )
    evento = Evento(
        titulo=evento_in.titulo,
        descripcion=evento_in.descripcion,
        inicio_evento=evento_in.inicio_evento,
        fin_evento=evento_in.fin_evento,
        capacidad_maxima=evento_in.capacidad_maxima,
        id_admin=admin_id,
    )
    db.add(evento)
    db.commit()
    db.refresh(evento)

    # Recalcular el estado de todas las solicitudes para actualizar pendientes -> parciales si intersectan
    recalcular_todas_las_solicitudes(db)

    # Notificar a las madres cuyas solicitudes intersecten
    solicitudes_intersectadas = (
        db.query(Solicitud)
        .options(joinedload(Solicitud.madre))
        .filter(
            Solicitud.inicio_requerido < evento.fin_evento,
            Solicitud.fin_requerido > evento.inicio_evento,
        )
        .all()
    )

    for sol in solicitudes_intersectadas:
        if sol.madre and sol.madre.correo:
            background_tasks.add_task(
                enviar_correo_solicitud_actualizada,
                email_destino=sol.madre.correo,
                nombre_madre=sol.madre.nombre,
                titulo_evento=evento.titulo,
                estado=sol.estado,
            )

    return evento


def reservar_cupo(
    db: Session,
    evento_id: uuid.UUID,
    solicitud_id: uuid.UUID,
    madre_id: uuid.UUID,
    background_tasks: BackgroundTasks,
) -> Reserva:
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe.",
        )

    solicitud = (
        db.query(Solicitud)
        .options(joinedload(Solicitud.madre))
        .filter(Solicitud.id == solicitud_id, Solicitud.madre_id == madre_id)
        .first()
    )
    if not solicitud:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La solicitud especificada no existe o no le pertenece.",
        )

    # Verificar aforo máximo
    total_reservas = db.query(func.count(Reserva.id)).filter(Reserva.evento_id == evento_id).scalar() or 0
    if total_reservas >= evento.capacidad_maxima:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aforo máximo alcanzado para este evento.",
        )

    # Verificar si ya existe reserva para esta solicitud
    reserva_existente = db.query(Reserva).filter(Reserva.solicitud_id == solicitud_id).first()
    if reserva_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta solicitud ya cuenta con una reserva confirmada.",
        )

    reserva = Reserva(evento_id=evento_id, solicitud_id=solicitud_id)
    db.add(reserva)
    db.commit()

    # Recalcular el estado exacto de la solicitud tras la reserva
    nuevo_estado = recalcular_estado_solicitud(db, solicitud)
    solicitud.estado = nuevo_estado
    db.add(solicitud)
    db.commit()
    db.refresh(reserva)

    if solicitud.madre and solicitud.madre.correo:
        background_tasks.add_task(
            enviar_correo_reserva_confirmada,
            email_destino=solicitud.madre.correo,
            nombre_madre=solicitud.madre.nombre,
            titulo_evento=evento.titulo,
            inicio_evento=evento.inicio_evento,
        )

    return reserva


def obtener_eventos_disponibles(db: Session) -> List[EventoResponse]:
    eventos = db.query(Evento).order_by(Evento.inicio_evento.asc()).all()
    resultado = []
    for ev in eventos:
        total_reservas = db.query(func.count(Reserva.id)).filter(Reserva.evento_id == ev.id).scalar() or 0
        cupos = max(0, ev.capacidad_maxima - total_reservas)
        ev_dict = EventoResponse.model_validate(ev)
        ev_dict.aforo_actual = total_reservas
        ev_dict.cupos_disponibles = cupos
        resultado.append(ev_dict)
    return resultado
