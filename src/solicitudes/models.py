import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

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
    menor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("menores.id", ondelete="CASCADE"),
        nullable=False,
    )
    inicio_requerido: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fin_requerido: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String, nullable=False, default="Pendiente")  # Pendiente, Parcial, Cubierta
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    madre = relationship("Usuario", back_populates="solicitudes")
    menor = relationship("Menor", back_populates="solicitudes")
    reservas = relationship("Reserva", back_populates="solicitud", cascade="all, delete-orphan")
