from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Department as DepartmentSchema, DepartmentCreate
from sqlalchemy import select
from db_depends import get_async_db
from models.department import Department as DepartmentModel
from models.employee import Employee as EmployeeModel
from crud import collect_sub_departments

router = APIRouter(prefix='/departments', tags=['departments'])

@router.post('/', response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
async def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новое подразделение.
    """
    if department.parent_id is not None:
        if not await db.scalar(select(DepartmentModel).where(DepartmentModel.id == department.parent_id)):
            raise HTTPException(status_code=404, detail="Родительское подразделение не найдено")
        
    db_department = DepartmentModel(**department.model_dump())
    db.add(db_department)
    await db.commit()
    return db_department

@router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_department(id: int,depth: int = Query(default=1, ge=1, le=5),include_employees: bool = Query(default=True),db: AsyncSession = Depends(get_async_db)):
    """ Получаем подразделение по id и иерархию по глубине с выводом сотрудников по необходимости"""

    department = await db.scalar(select(DepartmentModel).where(DepartmentModel.id == id))
    if not department:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")

    async def collect_sub_departments(parent_id: int, current_depth: int):

        result = await db.scalars(select(DepartmentModel).where(DepartmentModel.parent_id == parent_id))
        sub_deps = result.all()
        
        all_sub_deps = []
        for dep in sub_deps:
            all_sub_deps.append(dep)
            if current_depth > 1:
                children = await collect_sub_departments(dep.id, current_depth - 1)
                all_sub_deps.extend(children)
        
        return all_sub_deps

    sub_departments = await collect_sub_departments(department.id, depth)

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


async def has_cycle(db: AsyncSession, department_id: int, new_parent_id: int) -> bool:
    """
    Проверяет, не создаст ли установка new_parent_id цикл в иерархии.
    Обходит предков от new_parent_id вверх до корня.
    """
    if new_parent_id == department_id:
        return True  # Самоссылка

    current_id = new_parent_id
    visited = set()

    while current_id is not None:
        if current_id in visited:
            return True  # Цикл
        if current_id == department_id:
            return True  # Новый родитель — предок текущего подразделения

        parent_id = await db.scalar(select(DepartmentModel.parent_id).where(DepartmentModel.id == current_id))

        visited.add(current_id)
        current_id = parent_id

    return False

@router.patch('/{id}',response_model=DepartmentCreate, status_code=status.HTTP_200_OK)
async def update_department(id: int, department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)):
    stmt = await db.scalar(select(DepartmentModel).where(DepartmentModel.id == id))
    
    if not await db.scalar(select(DepartmentModel).where(DepartmentModel.id == id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подразделение не найдено"
        )
    if department.parent_id is not None:
        # Проверка на цикл
        if has_cycle(db, id, department.parent_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Некорректный parent_id: обнаружен цикл в иерархии подразделений"
            )

        # Проверяем существование родителя
        parent_stmt = select(DepartmentModel).where(DepartmentModel.id == department.parent_id)
        parent_result = await db.execute(parent_stmt)
        parent = parent_result.scalars().first()

        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительское подразделение не найдено"
            )

        department.parent_id = department.parent_id

    elif department.parent_id is None:
        # Явно снимаем родителя (делаем корневым)
        department.parent_id = None

    await db.commit()
    await db.refresh(department)
    return department
    
    


