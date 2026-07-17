from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.usuarios.models import Usuario
from src.usuarios.schemas import (
    Usuario as UsuarioSchema,
    UsuarioUpdate,
    ImpactoVoluntario,
    UsuarioOnboarding,
)
from src.inscripciones.models import Inscripcion as InscripcionModel
from src.eventos.models import Evento as EventoModel
from src.notificaciones.service import enviar_correo_bienvenida

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.delete("/me", status_code=status.HTTP_200_OK)
def dar_de_baja_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Da de baja al usuario actual anonimizando sus datos personales.

    Cumple con la normativa LFPDPPP (Derechos ARCO) evitando el borrado físico,
    lo que conserva la integridad de las estadísticas e inscripciones
    previas.
    """
    current_user.nombre = "Usuario Anonimizado"
    current_user.correo = f"anonimo_{str(current_user.id)}@sistema.com"
    current_user.telefono = "0000000000"
    current_user.activo = False

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar la baja y anonimización de datos: {str(e)}",
        )

    return {
        "status": "success",
        "message": "Cuenta dada de baja y datos anonimizados con éxito conforme a la normativa LFPDPPP.",
    }


@router.get("/me", response_model=UsuarioSchema)
def obtener_perfil_usuario(
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna la entidad del usuario autenticado actual."""
    return current_user


@router.patch("/me", response_model=UsuarioSchema)
def actualizar_perfil(
    update_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Actualiza campos opcionales del perfil del usuario actual (ej.

    teléfono, nombre).
    """
    if update_data.telefono is not None:
        current_user.telefono = update_data.telefono
    if update_data.nombre is not None:
        current_user.nombre = update_data.nombre

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el perfil: {str(e)}",
        )
    return current_user


@router.get("/me/impacto", response_model=ImpactoVoluntario)
def obtener_impacto_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Consulta las inscripciones del usuario actual donde asistió, cruzando

    con eventos para sumar la duración en horas y listar los eventos.
    """
    inscripciones = (
        db.query(InscripcionModel)
        .join(EventoModel, InscripcionModel.evento_id == EventoModel.id)
        .filter(
            InscripcionModel.usuario_id == current_user.id,
            InscripcionModel.asistio.is_(True),
            EventoModel.fecha_fin < func.now(),
        )
        .all()
    )

    eventos_asistidos = [ins.evento for ins in inscripciones]
    total_horas = sum(evt.duracion_horas for evt in eventos_asistidos)
    total_eventos = len(eventos_asistidos)

    # Inyectar atributos calculados requeridos por el esquema EventoSchema para evitar errores de validación
    for evt in eventos_asistidos:
        conteo = db.query(InscripcionModel).filter(InscripcionModel.evento_id == evt.id).count()
        evt.cupos_disponibles = max(0, evt.cupo_maximo - conteo)
        evt.usuario_inscrito = True

    return {
        "total_horas": total_horas,
        "total_eventos": total_eventos,
        "eventos_asistidos": eventos_asistidos
    }


@router.post("/me/onboarding", response_model=UsuarioSchema)
def completar_onboarding(
    datos: UsuarioOnboarding,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Procesa la información del flujo de onboarding del voluntario,

    actualizando sus datos obligatorios y encolando el correo de bienvenida.
    """
    current_user.nombre = datos.nombre
    current_user.fecha_nacimiento = datos.fecha_nacimiento
    current_user.sexo = datos.sexo
    current_user.telefono = datos.telefono

    try:
        db.commit()
        db.refresh(current_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar datos de onboarding: {str(e)}",
        )

    background_tasks.add_task(enviar_correo_bienvenida, current_user.correo, datos.nombre)

    return current_user
