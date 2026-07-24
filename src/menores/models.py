import uuid
from datetime import date, datetime, timezone
from sqlalchemy import Date, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Menor(Base):
    __tablename__ = "menores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    madre_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String, nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    alergias: Mapped[str | None] = mapped_column(Text, nullable=True, default="Ninguna")
    requerimientos_medicos: Mapped[str | None] = mapped_column(Text, nullable=True, default="Ninguno")
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    madre = relationship("Usuario", back_populates="menores")
    solicitudes = relationship("Solicitud", back_populates="menor", cascade="all, delete-orphan")
