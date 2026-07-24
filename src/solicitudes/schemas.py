import uuid
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from src.menores.schemas import MenorResponse


class SolicitudBase(BaseModel):
    menor_id: uuid.UUID
    inicio_requerido: datetime
    fin_requerido: datetime

    @model_validator(mode="after")
    def validar_rango_horario(self):
        if self.inicio_requerido.tzinfo is None:
            self.inicio_requerido = self.inicio_requerido.replace(tzinfo=timezone.utc)
        if self.fin_requerido.tzinfo is None:
            self.fin_requerido = self.fin_requerido.replace(tzinfo=timezone.utc)

        if self.inicio_requerido >= self.fin_requerido:
            raise ValueError("El horario de inicio debe ser estrictamente anterior al horario de fin.")
        return self


class SolicitudCreate(SolicitudBase):
    pass


class SolicitudResponse(SolicitudBase):
    id: uuid.UUID
    madre_id: uuid.UUID
    estado: str
    creado_en: datetime
    menor: Optional[MenorResponse] = None

    model_config = ConfigDict(from_attributes=True)
