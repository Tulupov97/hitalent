from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from database import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    depatment_id: Mapped[int] = mapped_column(Integer, ForeignKey('departments.id'))
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    positoinion: Mapped[str] = mapped_column(String(50), nullable=False)
    hired_at: Mapped[DateTime|None] = mapped_column(DateTime)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now())

    departments: Mapped['Department'] = relationship("Department", back_populates='employees')




