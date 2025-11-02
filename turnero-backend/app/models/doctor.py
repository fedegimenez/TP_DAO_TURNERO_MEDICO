from datetime import time
from datetime import time

from sqlalchemy import String, Boolean, Table, Column, ForeignKey, Integer, Time, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


doctor_specialty = Table(
    "doctor_specialties",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("doctors.id", ondelete="CASCADE"), primary_key=True),
    Column("specialty_id", Integer, ForeignKey("specialties.id", ondelete="RESTRICT"), primary_key=True),
)


class Doctor(Base):
    __tablename__ = "doctors"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(80))
    apellido: Mapped[str] = mapped_column(String(80))
    dni: Mapped[str] = mapped_column(String(20), index=True)
    genero: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(30), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    matricula: Mapped[str] = mapped_column(String(40), unique=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    specialties = relationship("Specialty", secondary=doctor_specialty, lazy="selectin")
    availability = relationship(
        "DoctorAvailability",
        back_populates="doctor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"))
    day_of_week: Mapped[int] = mapped_column(SmallInteger)  # 0=Monday
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    slot_minutes: Mapped[int] = mapped_column(Integer, default=30)

    doctor = relationship("Doctor", back_populates="availability")

    def contains(self, candidate: time) -> bool:
        return self.start_time <= candidate < self.end_time
