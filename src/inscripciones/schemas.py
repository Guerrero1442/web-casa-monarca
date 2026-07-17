from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from src.usuarios.schemas import Usuario


class InscripcionBase(BaseModel):
    usuario_id: UUID
    evento_id: UUID


class InscripcionCreate(InscripcionBase):
    pass


class InscripcionUpdate(BaseModel):
    asistio: bool | None = None


class Inscripcion(InscripcionBase):
    id: UUID
    asistio: bool
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class InscripcionConUsuario(Inscripcion):
    """Representa una inscripción incluyendo los detalles del usuario

    asociado.
    """

    usuario: Usuario


class AsistenciaBulkUpdate(BaseModel):
    """Cuerpo de solicitud para actualizar la asistencia de múltiples

    inscripciones de manera masiva.
    """

    inscripcion_ids: list[UUID]
