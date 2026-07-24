import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class MenorBase(BaseModel):
    nombre: str
    fecha_nacimiento: date
    alergias: str | None = "Ninguna"
    requerimientos_medicos: str | None = "Ninguno"


class MenorCreate(MenorBase):
    pass


class MenorResponse(MenorBase):
    id: uuid.UUID
    madre_id: uuid.UUID
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
