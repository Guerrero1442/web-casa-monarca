import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Boolean, DateTime, String, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.database import Base


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
    telefono: Mapped[str | None] = mapped_column(String, nullable=True)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)
    sexo: Mapped[str | None] = mapped_column(String, nullable=True)
    rol: Mapped[str] = mapped_column(String, nullable=False, default="madre")  # admin, madre
    proveedor_auth: Mapped[str] = mapped_column(String, nullable=False, default="email")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    menores = relationship(
        "Menor",
        back_populates="madre",
        cascade="all, delete-orphan",
    )
    solicitudes = relationship(
        "Solicitud",
        back_populates="madre",
        cascade="all, delete-orphan",
    )
