from datetime import date
from sqlalchemy import ForeignKey, String, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Prescription(Base):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    consultation_id: Mapped[int] = mapped_column(ForeignKey("consultations.id", ondelete="CASCADE"))
    fecha_emision: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVA")
    firma_digital: Mapped[str | None] = mapped_column(String(200), nullable=True)

    consultation = relationship("Consultation", back_populates="prescriptions")
    items = relationship("PrescriptionItem", cascade="all, delete-orphan", back_populates="prescription")


class PrescriptionItem(Base):
    __tablename__ = "prescription_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    prescription_id: Mapped[int] = mapped_column(ForeignKey("prescriptions.id", ondelete="CASCADE"))
    medicamento: Mapped[str] = mapped_column(String(200))
    dosis: Mapped[str | None] = mapped_column(String(160), nullable=True)
    frecuencia: Mapped[str | None] = mapped_column(String(160), nullable=True)
    duracion: Mapped[str | None] = mapped_column(String(160), nullable=True)
    indicaciones: Mapped[str | None] = mapped_column(Text, nullable=True)

    prescription = relationship("Prescription", back_populates="items")
