import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator


class EventoBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    inicio_evento: datetime
    fin_evento: datetime
    capacidad_maxima: int

    @model_validator(mode="after")
    def validar_rango_horario_evento(self):
        if self.inicio_evento >= self.fin_evento:
            raise ValueError("El horario de inicio debe ser estrictamente anterior al horario de fin del evento.")
        if self.capacidad_maxima <= 0:
            raise ValueError("La capacidad máxima debe ser mayor a cero.")
        return self


class EventoCreate(EventoBase):
    pass


class ReservaResponse(BaseModel):
    id: uuid.UUID
    evento_id: uuid.UUID
    solicitud_id: uuid.UUID
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class EventoResponse(EventoBase):
    id: uuid.UUID
    id_admin: uuid.UUID
    creado_en: datetime
    aforo_actual: int = 0
    cupos_disponibles: int = 0

    model_config = ConfigDict(from_attributes=True)
