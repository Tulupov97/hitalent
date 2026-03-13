from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название подразделения")
    parent_id: int | None = Field(default=None, description="ID родительского подразделения")

class Department(DepartmentCreate):
    id: int = Field(..., description="ID подразделения")
    created_at: datetime = Field(..., description="Дата создания подразделения")

    model_config = ConfigDict(from_attributes=True)

class EmployeeCreate(BaseModel):
    department_id: int = Field(..., description="ID подразделения")
    full_name: str = Field(..., min_length=1, max_length=200, description="ФИО сотрудника")
    position: str = Field(..., min_length=1, max_length=200, description="Должность сотрудника")
    hired_at: date | None = Field(default=None, description="Дата приема на работу")

class Employee(EmployeeCreate):
    id: int = Field(..., description="ID сотрудника")
    created_at: datetime = Field(..., description="Дата создания")

