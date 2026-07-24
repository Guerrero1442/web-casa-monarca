import uuid
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.eventos.schemas import EventoCreate, EventoResponse, ReservaResponse
from src.eventos.service import cancelar_reserva, crear_evento, obtener_eventos_disponibles, reservar_cupo
from src.usuarios.models import Usuario

router = APIRouter(prefix="/eventos", tags=["eventos"])


@router.post("/", response_model=EventoResponse, status_code=status.HTTP_201_CREATED)
def endpoint_crear_evento(
    evento_in: EventoCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación denegada: Solo los administradores pueden crear eventos.",
        )

    evento = crear_evento(
        db=db,
        evento_in=evento_in,
        admin_id=usuario_actual.id,
        background_tasks=background_tasks,
    )
    ev_response = EventoResponse.model_validate(evento)
    ev_response.aforo_actual = 0
    ev_response.cupos_disponibles = evento.capacidad_maxima
    return ev_response


@router.get("/", response_model=List[EventoResponse])
def endpoint_listar_eventos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return obtener_eventos_disponibles(db=db)


@router.post("/{evento_id}/reservar", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def endpoint_reservar_cupo(
    evento_id: uuid.UUID,
    solicitud_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    reserva = reservar_cupo(
        db=db,
        evento_id=evento_id,
        solicitud_id=solicitud_id,
        madre_id=usuario_actual.id,
        background_tasks=background_tasks,
    )
    return reserva


@router.delete("/reservas/{reserva_id}")
def endpoint_cancelar_reserva(
    reserva_id: uuid.UUID,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return cancelar_reserva(db=db, reserva_id=reserva_id, usuario_actual=usuario_actual)
