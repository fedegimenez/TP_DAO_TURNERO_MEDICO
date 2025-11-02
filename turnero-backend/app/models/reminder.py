from datetime import datetime
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"))
    canal: Mapped[str] = mapped_column(String(20))
    programado_para: Mapped[datetime] = mapped_column(DateTime)
    enviado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE")
    error_msg: Mapped[str | None] = mapped_column(String(200), nullable=True)

    appointment = relationship("Appointment", back_populates="reminders")
