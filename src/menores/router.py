from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.dependencies import get_current_user
from src.database import get_db
from src.menores.models import Menor
from src.menores.schemas import MenorCreate, MenorResponse
from src.usuarios.models import Usuario

router = APIRouter(prefix="/menores", tags=["menores"])


@router.post("/", response_model=MenorResponse, status_code=status.HTTP_201_CREATED)
def registrar_menor(
    menor_in: MenorCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    menor = Menor(
        madre_id=usuario_actual.id,
        nombre=menor_in.nombre,
        fecha_nacimiento=menor_in.fecha_nacimiento,
        alergias=menor_in.alergias or "Ninguna",
        requerimientos_medicos=menor_in.requerimientos_medicos or "Ninguno",
    )
    db.add(menor)
    db.commit()
    db.refresh(menor)
    return menor


@router.get("/", response_model=List[MenorResponse])
def listar_mis_menores(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_current_user),
):
    return db.query(Menor).filter(Menor.madre_id == usuario_actual.id).all()
