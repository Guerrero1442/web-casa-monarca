import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator


class MenorBase(BaseModel):
    nombre: str
    fecha_nacimiento: date
    alergias: Optional[str] = None
    requerimientos_medicos: Optional[str] = None

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_edad_menor(cls, fecha_nac: date) -> date:
        hoy = date.today()
        # Calcular fecha limite de 18 años
        try:
            hace_18_anos = date(hoy.year - 18, hoy.month, hoy.day)
        except ValueError:
            # Manejo de año bisiesto (29 de feb)
            hace_18_anos = date(hoy.year - 18, hoy.month, 28)

        if fecha_nac <= hace_18_anos:
            raise ValueError("El registro está restringido a menores de edad (menos de 18 años).")
        if fecha_nac > hoy:
            raise ValueError("La fecha de nacimiento no puede estar en el futuro.")
        return fecha_nac


class MenorCreate(MenorBase):
    pass


class MenorResponse(MenorBase):
    id: uuid.UUID
    madre_id: uuid.UUID
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
