from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.usuarios.models import Usuario
from src.usuarios.schemas import (
    Usuario as UsuarioSchema,
    UsuarioUpdate,
    UsuarioOnboarding,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.delete("/me", status_code=status.HTTP_200_OK)
def dar_de_baja_usuario(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Da de baja al usuario actual anonimizando sus datos personales (LFPDPPP)."""
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
    """Actualiza campos opcionales del perfil del usuario actual."""
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


@router.post("/me/onboarding", response_model=UsuarioSchema)
def completar_onboarding(
    datos: UsuarioOnboarding,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Procesa la información del flujo de onboarding del usuario."""
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

    return current_user
