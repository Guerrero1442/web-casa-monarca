import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Boolean, DateTime, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base
from src.inscripciones.models import Inscripcion  # noqa: F401


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    correo: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)  # Puede ser nulo con Google/Facebook login
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String, nullable=True)
    rol: Mapped[str] = mapped_column(String, nullable=False, default="voluntario")  # admin, voluntario
    proveedor_auth: Mapped[str] = mapped_column(String, nullable=False, default="email")  # email, google, facebook
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)  # Para bajas lógicas (Derechos ARCO)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relación con Inscripciones
    inscripciones = relationship(
        "Inscripcion",
        back_populates="usuario",
        cascade="all, delete-orphan",
    )
