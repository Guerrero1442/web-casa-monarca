from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.menores.models import Menor
from src.solicitudes.models import Solicitud
from src.solicitudes.schemas import SolicitudCreate, SolicitudResponse
from src.usuarios.models import Usuario

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.post("/", response_model=SolicitudResponse, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    solicitud_in: SolicitudCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    # Verificar que el menor pertenezca a la madre autenticada
    menor = db.query(Menor).filter(
        Menor.id == solicitud_in.menor_id,
        Menor.madre_id == usuario_actual.id,
    ).first()
    if not menor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El menor especificado no existe o no está registrado bajo su cuenta.",
        )

    solicitud = Solicitud(
        madre_id=usuario_actual.id,
        menor_id=solicitud_in.menor_id,
        inicio_requerido=solicitud_in.inicio_requerido,
        fin_requerido=solicitud_in.fin_requerido,
        estado="Pendiente",
    )
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router.get("/", response_model=List[SolicitudResponse])
def listar_mis_solicitudes(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return (
        db.query(Solicitud)
        .options(joinedload(Solicitud.menor))
        .filter(Solicitud.madre_id == usuario_actual.id)
        .order_by(Solicitud.inicio_requerido.desc())
        .all()
    )


@router.get("/consolidadas", response_model=List[SolicitudResponse])
def listar_solicitudes_consolidadas(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    if usuario_actual.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: solo administradores pueden ver solicitudes consolidadas.",
        )
    return (
        db.query(Solicitud)
        .options(joinedload(Solicitud.menor))
        .order_by(Solicitud.inicio_requerido.asc())
        .all()
    )
