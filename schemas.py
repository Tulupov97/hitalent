from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Название подразделения")
    parent_id: int | None = Field(None, description="ID родительского подразделения")

class Department(DepartmentCreate):
    id: int = Field(..., description="ID подразделения")
    created_at: datetime = Field(..., description="Дата создания подразделения")

    model_config = ConfigDict(from_attributes=True)


