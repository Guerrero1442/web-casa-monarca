from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from src.auth.dependencies import require_phone_verified
from src.database import get_db
from src.eventos.models import Evento
from src.inscripciones.models import Inscripcion as InscripcionModel
from src.inscripciones.schemas import Inscripcion as InscripcionSchema, InscripcionCreate
from src.usuarios.models import Usuario
from src.notificaciones.service import enviar_correo_inscripcion

router = APIRouter(prefix="/inscripciones", tags=["Inscripciones"])


@router.post(
    "/",
    response_model=InscripcionSchema,
    status_code=status.HTTP_201_CREATED,
)
def registrar_inscripcion(
    inscripcion: InscripcionCreate,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(require_phone_verified),
    db: Session = Depends(get_db),
):
    """Inscribe al usuario actual en un evento utilizando control de

    concurrencia atómico (bloqueo de fila), y despacha un correo de
    confirmación en segundo plano.
    """
    # 1. Verificar permisos: El usuario no puede inscribir a otra persona y los administradores no pueden registrarse
    if current_user.rol == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación denegada: Los administradores no pueden registrarse en eventos.",
        )

    if current_user.id != inscripcion.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para registrar inscripciones para otro usuario.",
        )

    # 2. Iniciar el bloqueo transaccional sobre la fila del evento
    # Esto serializa las inscripciones concurrentes para un mismo evento.
    evento = (
        db.query(Evento)
        .filter(Evento.id == inscripcion.evento_id)
        .with_for_update()
        .first()
    )

    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe.",
        )

    # Restricción de ciclo de vida: Bloqueo de mutabilidad si el evento ya inició
    from datetime import datetime, timezone
    if evento.fecha_inicio <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operación denegada: El evento ya está en curso o ha finalizado.",
        )

    # 3. Comprobar si ya existe una inscripción para este usuario y evento
    # Evita violaciones de la UniqueConstraint uq_usuario_evento
    inscripcion_existente = (
        db.query(InscripcionModel)
        .filter(
            InscripcionModel.usuario_id == current_user.id,
            InscripcionModel.evento_id == inscripcion.evento_id,
        )
        .first()
    )

    if inscripcion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya te encuentras inscrito en este evento.",
        )

    # 4. Evaluar el cupo máximo
    cupos_ocupados = (
        db.query(InscripcionModel)
        .filter(InscripcionModel.evento_id == inscripcion.evento_id)
        .count()
    )

    if cupos_ocupados >= evento.cupo_maximo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay cupos disponibles para este evento. Capacidad máxima alcanzada.",
        )

    # 5. Registrar la inscripción
    db_inscripcion = InscripcionModel(
        usuario_id=current_user.id,
        evento_id=inscripcion.evento_id,
        asistio=False,
    )
    db.add(db_inscripcion)

    try:
        db.commit()
        db.refresh(db_inscripcion)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al confirmar la inscripción: {str(e)}",
        )

    # 6. Agendar en segundo plano el envío del correo de confirmación
    background_tasks.add_task(
        enviar_correo_inscripcion,
        current_user.correo,
        current_user.nombre,
        evento.titulo,
        evento.fecha_inicio,
    )

    return db_inscripcion
