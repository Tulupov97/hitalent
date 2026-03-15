from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Department as DepartmentSchema, DepartmentCreate
from sqlalchemy import select
from db_depends import get_async_db
from models.employee import Employee as EmployeeModel
from crud import check_department, collect_sub_departments, create_department, check_parent, has_cycle, check_name, delete_department

router = APIRouter(prefix='/departments', tags=['departments'])

@router.post('/', response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
async def create_department_endpoint(
    department: DepartmentCreate,
    db: AsyncSession = Depends(get_async_db)
):
    if department.parent_id is not None:
        await check_parent(department.parent_id, db)
    return await create_department(department, db)

@router.get('/{id}',status_code=status.HTTP_200_OK)
async def get_department(id: int,
                        depth: int = Query(default=1, ge=1, le=5),
                        include_employees: bool = Query(default=True),
                        db: AsyncSession = Depends(get_async_db)):
    """ Получаем подразделение по id и иерархию по глубине с выводом сотрудников по необходимости"""

    department = await check_department(id, db)

    sub_departments = await collect_sub_departments(department.id, depth, db)

    employees = []
    if include_employees:
        emp_result = await db.scalars(
            select(EmployeeModel)
            .where(EmployeeModel.department_id == id).order_by(EmployeeModel.full_name)
        )
        employees = emp_result.all()

    return {
        'department': department,
        'sub_departments': sub_departments,
        'employees': employees if include_employees else []
    }


@router.patch('/{id}',response_model=DepartmentCreate, status_code=status.HTTP_200_OK)
async def update_department(id: int, department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)):
    department_db = await check_department(id, db)

    if department.parent_id == id:
        raise HTTPException(
            status_code=400,
        detail='Нельзя назначить категорию родителем самого себя')
    
    if department.parent_id is not None:
        await check_parent(department.parent_id, db)
        await check_name(department, db)
        await has_cycle(id,department.parent_id,db)

    department_db.parent_id = department.parent_id
    department_db.name = department.name
    await db.commit()
    await db.refresh(department_db)
    return department_db


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_department_endpoint(
    id: int,
    mode: str = Query(..., pattern='^(cascade|reassign)$'),
    reassign_to_department_id: int | None = None,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Удаляет подразделение по id.
    - mode=cascade: удаляет подразделение, его сотрудников и все дочерние подразделения.
    - mode=reassign: удаляет подразделение, но сотрудников перемещает в другое подразделение.
      В этом случае reassign_to_department_id обязателен.
    """
    await delete_department(id, mode, reassign_to_department_id, db)
    return
