from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class EventoBase(BaseModel):
    titulo: str
    descripcion: str | None = None
    fecha_inicio: datetime
    fecha_fin: datetime
    duracion_horas: float = Field(default=0.0, ge=0.0)
    cupo_maximo: int = Field(gt=0)
    lugar: str


class EventoCreate(EventoBase):
    id_admin: UUID


class EventoUpdate(BaseModel):
    titulo: str | None = None
    descripcion: str | None = None
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    duracion_horas: float | None = Field(default=None, ge=0.0)
    cupo_maximo: int | None = Field(default=None, gt=0)
    lugar: str | None = None
    id_admin: UUID | None = None


class Evento(EventoBase):
    id: UUID
    id_admin: UUID
    creado_en: datetime
    cupos_disponibles: int
    usuario_inscrito: bool

    model_config = ConfigDict(from_attributes=True)
