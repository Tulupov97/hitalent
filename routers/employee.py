from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Employee as EmployeeSchema, EmployeeCreate
from sqlalchemy import select
from db_depends import get_async_db
from models.department import Department as DepartmentModel
from models.employee import Employee as EmployeeModel

router = APIRouter(prefix='/employees', tags=['employees'])

@router.post('/departments/{id}', response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
async def create_department(id: int, employee: EmployeeCreate, db: AsyncSession = Depends(get_async_db)):

    """
    Создать сотрудника в подразделении.
    """
    if not await db.scalar(select(DepartmentModel).where(DepartmentModel.id == id)):
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    
    db_employee = EmployeeModel(**employee.model_dump())
    db.add(db_employee)
    await db.commit()
    return db_employee
