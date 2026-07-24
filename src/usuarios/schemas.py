from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UsuarioBase(BaseModel):
    nombre: str
    correo: str


class UsuarioCreate(UsuarioBase):
    telefono: str | None = None
    rol: str = "madre"
    proveedor_auth: str = "email"


class UsuarioUpdate(BaseModel):
    nombre: str | None = None
    correo: str | None = None
    telefono: str | None = None
    rol: str | None = None
    proveedor_auth: str | None = None
    activo: bool | None = None


class Usuario(UsuarioBase):
    id: UUID
    telefono: str | None
    fecha_nacimiento: date | None = None
    sexo: str | None = None
    rol: str
    proveedor_auth: str
    activo: bool
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)


class UsuarioOnboarding(BaseModel):
    nombre: str
    fecha_nacimiento: date
    sexo: str
    telefono: str
