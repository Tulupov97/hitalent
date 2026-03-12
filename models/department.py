from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from database import Base
from datetime import datetime

class Department(Base):
    __tablename__ = 'departments'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('departments.id'), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now())

    parent: Mapped['Department | None'] = relationship("Department", back_populates='children', remote_side='Depatment.id')

    children: Mapped[list['Department']] = relationship("Department", back_populates='parent')

    employees: Mapped[list['Employee']] = relationship("Employee", back_populates='departments')


