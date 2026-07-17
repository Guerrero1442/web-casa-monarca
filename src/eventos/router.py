from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from src.auth.dependencies import require_role, get_current_user_opcional, get_current_user
from src.database import get_db
from src.eventos.models import Evento as EventoModel
from src.eventos.schemas import Evento as EventoSchema, EventoCreate, EventoUpdate
from src.inscripciones.models import Inscripcion as InscripcionModel
from src.inscripciones.schemas import InscripcionConUsuario, AsistenciaBulkUpdate
from src.notificaciones.service import enviar_correo_asistencia
from src.usuarios.models import Usuario

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "/",
    response_model=EventoSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(["admin"]))],
)
def crear_evento(evento: EventoCreate, db: Session = Depends(get_db)):
    """Crea un nuevo evento en el sistema.

    Solo accesible para usuarios con rol 'admin'.
    """
    db_evento = EventoModel(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)

    # Inyectar propiedades calculadas iniciales para evitar ResponseValidationError
    db_evento.cupos_disponibles = db_evento.cupo_maximo
    db_evento.usuario_inscrito = False

    return db_evento


@router.get("/", response_model=list[EventoSchema])
def listar_eventos(
    db: Session = Depends(get_db),
    current_user: Usuario | None = Depends(get_current_user_opcional),
):
    """Lista todos los eventos registrados en el sistema, calculando dinámicamente

    los cupos disponibles y si el usuario actual se encuentra inscrito.
    """
    # Subconsulta para contar inscripciones por evento
    subquery = (
        db.query(
            InscripcionModel.evento_id,
            func.count(InscripcionModel.id).label("conteo_inscritos"),
        )
        .group_by(InscripcionModel.evento_id)
        .subquery()
    )

    # Consulta de eventos con conteo de inscritos usando outerjoin
    eventos_con_conteo = (
        db.query(
            EventoModel,
            func.coalesce(subquery.c.conteo_inscritos, 0).label("conteo"),
        )
        .outerjoin(subquery, EventoModel.id == subquery.c.evento_id)
        .all()
    )

    usuario_id = current_user.id if current_user else None

    # Obtener el conjunto de IDs de eventos en los que el usuario ya está inscrito para evitar consultas N+1
    eventos_inscritos_ids = set()
    if usuario_id:
        inscripciones_usuario = (
            db.query(InscripcionModel.evento_id)
            .filter(InscripcionModel.usuario_id == usuario_id)
            .all()
        )
        eventos_inscritos_ids = {ins.evento_id for ins in inscripciones_usuario}

    eventos_response = []
    for db_evento, conteo in eventos_con_conteo:
        cupos_disp = max(0, db_evento.cupo_maximo - conteo)
        inscrito = db_evento.id in eventos_inscritos_ids

        evento_dict = {
            "id": db_evento.id,
            "titulo": db_evento.titulo,
            "descripcion": db_evento.descripcion,
            "fecha_inicio": db_evento.fecha_inicio,
            "fecha_fin": db_evento.fecha_fin,
            "duracion_horas": db_evento.duracion_horas,
            "cupo_maximo": db_evento.cupo_maximo,
            "lugar": db_evento.lugar,
            "id_admin": db_evento.id_admin,
            "creado_en": db_evento.creado_en,
            "cupos_disponibles": cupos_disp,
            "usuario_inscrito": inscrito,
        }
        eventos_response.append(evento_dict)

    return eventos_response


@router.get(
    "/{evento_id}/inscritos",
    response_model=list[InscripcionConUsuario],
    dependencies=[Depends(require_role(["admin"]))],
)
def obtener_inscritos(evento_id: UUID, db: Session = Depends(get_db)):
    """Obtiene la lista de inscritos para un evento específico.

    Solo accesible para administradores.
    """
    evento = db.query(EventoModel).filter(EventoModel.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe.",
        )

    inscripciones = (
        db.query(InscripcionModel)
        .filter(InscripcionModel.evento_id == evento_id)
        .all()
    )
    return inscripciones


@router.put(
    "/{evento_id}/asistencia",
    dependencies=[Depends(require_role(["admin"]))],
)
def actualizar_asistencia_masiva(
    evento_id: UUID,
    asistencia: AsistenciaBulkUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Marca la asistencia como True para un listado masivo de inscripciones de

    un evento, y encola el envío de correos de agradecimiento/impacto.

    Solo accesible para administradores.
    """
    evento = db.query(EventoModel).filter(EventoModel.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe.",
        )

    from datetime import datetime, timezone
    if evento.fecha_fin > datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede marcar asistencia para un evento que no ha finalizado",
        )

    # 1. Obtener las inscripciones usando joinedload para evitar consultas N+1 al acceder a inscripcion.usuario
    inscripciones = (
        db.query(InscripcionModel)
        .options(joinedload(InscripcionModel.usuario))
        .filter(
            InscripcionModel.evento_id == evento_id,
            InscripcionModel.id.in_(asistencia.inscripcion_ids),
        )
        .all()
    )

    if not inscripciones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontraron inscripciones que coincidan con los IDs proporcionados.",
        )

    actualizados = 0
    tareas_correo: list[tuple[str, str, str]] = []

    # 2. Actualizar los registros en la base de datos y acumular la información de correos
    for inscripcion in inscripciones:
        if not inscripcion.asistio:
            inscripcion.asistio = True
            actualizados += 1

            # Acumular datos para el envío de correos fuera del ciclo transaccional
            tareas_correo.append(
                (
                    inscripcion.usuario.correo,
                    inscripcion.usuario.nombre,
                    evento.titulo,
                )
            )

    # 3. Confirmar la transacción en la base de datos
    if actualizados > 0:
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al guardar la asistencia masiva: {str(e)}",
            )

    # 4. Encolar los correos en segundo plano estrictamente después del commit exitoso
    for correo, nombre, titulo in tareas_correo:
        background_tasks.add_task(
            enviar_correo_asistencia,
            correo,
            nombre,
            titulo,
        )

    return {
        "status": "success",
        "message": f"Se actualizo la asistencia de {actualizados} inscritos exitosamente.",
    }


@router.patch("/{evento_id}", response_model=EventoSchema)
def actualizar_evento(
    evento_id: UUID,
    evento_data: EventoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"])),
):
    """Actualiza los atributos de un evento. Solo accesible para administradores."""
    db_evento = db.query(EventoModel).filter(EventoModel.id == evento_id).first()
    if not db_evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado",
        )

    # Restricción de ciclo de vida: Bloqueo de mutabilidad si el evento ya inició
    from datetime import datetime, timezone
    if db_evento.fecha_inicio <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operación denegada: El evento ya está en curso o ha finalizado.",
        )
    
    # Actualizar solo los campos provistos
    update_data = evento_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_evento, key, value)
        
    try:
        db.commit()
        db.refresh(db_evento)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el evento: {str(e)}",
        )
        
    conteo = db.query(InscripcionModel).filter(InscripcionModel.evento_id == db_evento.id).count()
    cupos_disp = max(0, db_evento.cupo_maximo - conteo)
    
    inscrito = False
    if current_user:
        inscrito = db.query(InscripcionModel).filter(
            InscripcionModel.evento_id == db_evento.id,
            InscripcionModel.usuario_id == current_user.id
        ).first() is not None

    db_evento.cupos_disponibles = cupos_disp
    db_evento.usuario_inscrito = inscrito
    
    return db_evento


@router.delete("/{evento_id}/inscripcion", status_code=status.HTTP_200_OK)
def cancelar_inscripcion(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cancela la inscripción del voluntario actual a un evento."""
    # Consultar el evento para verificar ciclo de vida
    evento = db.query(EventoModel).filter(EventoModel.id == evento_id).first()
    if not evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El evento especificado no existe.",
        )

    from datetime import datetime, timezone
    if evento.fecha_inicio <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Operación denegada: El evento ya está en curso o ha finalizado.",
        )

    inscripcion = (
        db.query(InscripcionModel)
        .filter(
            InscripcionModel.evento_id == evento_id,
            InscripcionModel.usuario_id == current_user.id,
        )
        .first()
    )
    
    if not inscripcion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No estás inscrito en este evento",
        )
        
    if inscripcion.asistio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una inscripción de un evento al que ya asististe",
        )
        
    try:
        db.delete(inscripcion)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar la inscripción: {str(e)}",
        )

    return {"status": "success", "message": "Inscripción cancelada exitosamente"}


@router.delete("/{evento_id}", status_code=status.HTTP_200_OK)
def eliminar_evento(
    evento_id: UUID,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role(["admin"])),
):
    """Elimina un evento de la base de datos. Solo accesible para administradores.

    Las inscripciones asociadas se eliminarán en cascada.
    """
    db_evento = db.query(EventoModel).filter(EventoModel.id == evento_id).first()
    if not db_evento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento no encontrado",
        )

    try:
        db.delete(db_evento)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el evento: {str(e)}",
        )
    return {"status": "success", "message": "Evento eliminado con éxito"}

