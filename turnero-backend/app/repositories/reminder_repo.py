from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.reminder import Reminder


class ReminderRepo:
    @staticmethod
    def upcoming_for_appointment(db: Session, appointment_id: int) -> List[Reminder]:
        stmt = select(Reminder).where(Reminder.appointment_id == appointment_id).order_by(Reminder.programado_para)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def create(db: Session, **data) -> Reminder:
        reminder = Reminder(**data)
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder
