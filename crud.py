from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db_depends import get_async_db
from models.department import Department as DepartmentModel
from schemas import DepartmentCreate
from models.employee import Employee as EmployeeModel

async def check_department(department_id : int, db: AsyncSession = Depends(get_async_db)) -> DepartmentModel | None:
    """Проверка существоания департамента"""
    if not await db.scalar(select(DepartmentModel).where(DepartmentModel.id == department_id)):
        raise HTTPException(status_code=404, detail="Подразделение не найдено")
    return await db.scalar(select(DepartmentModel).where(DepartmentModel.id == department_id))
    

async def collect_sub_departments(parent_id: int, current_depth: int, db: AsyncSession = Depends(get_async_db)) -> list[DepartmentModel]:
        """Функция сбора подразделений-наследников для patch эндпоинта"""

        result = await db.scalars(select(DepartmentModel).where(DepartmentModel.parent_id == parent_id))
        sub_deps = result.all()
        
        all_sub_deps = []
        for dep in sub_deps:
            all_sub_deps.append(dep)
            if current_depth > 1:
                children = await collect_sub_departments(dep.id, current_depth - 1)
                all_sub_deps.extend(children)
        
        return all_sub_deps

async def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)) -> DepartmentModel:
    """
    Создаёт новое подразделение.
    """
    if department.parent_id is not None:
        await check_parent(department.parent_id, db)
        await check_name(department, db)
        
    db_department = DepartmentModel(**department.model_dump())
    db.add(db_department)
    await db.commit()
    return db_department

async def check_parent(department_id: int, db: AsyncSession = Depends(get_async_db)) -> None:
        if not await db.scalar(select(DepartmentModel).where(DepartmentModel.id == department_id)):
                raise HTTPException(status_code=404, detail="Подразделение-родитель не найдено")
        

async def has_cycle(id: int, target_parent_id: int, db: AsyncSession = Depends(get_async_db)) -> None:
    """
    Проверяет, приведёт ли установка parent_id=target_parent_id к циклу в дереве.
    """

    ancestors = set()
    current_id = target_parent_id
    while current_id is not None:
        ancestors.add(current_id)
        parent_id = await db.scalar(
            select(DepartmentModel.parent_id).where(DepartmentModel.id == current_id)
        )
        current_id = parent_id

    if id in ancestors:
         raise HTTPException(
            status_code=409,
            detail="Нельзя создать цикл в дереве"
        )
        
async def delete_department(
    department_id: int,
    mode: str,
    reassign_to_department_id: int | None,
    db: AsyncSession
):
    # Получаем подразделение
    department = await check_department(department_id, db)
    if not department:
        raise HTTPException(status_code=404, detail="Подразделение не найдено")

    if mode == "cascade":
        await db.delete(department)
    
    elif mode == "reassign":
        if not reassign_to_department_id:
            raise HTTPException(status_code=400, detail="reassign_to_department_id обязателен при mode=reassign")
        
        reassign_to = await check_department(reassign_to_department_id, db)
        if not reassign_to:
            raise HTTPException(status_code=404, detail="Целевое подразделение для перевода не найдено")

        # Переназначаем сотрудников
        await db.execute(
            update(EmployeeModel)
            .where(EmployeeModel.department_id == department_id)
            .values(department_id=reassign_to_department_id)
        )
        
        await db.delete(department)
    
    else:
        raise HTTPException(status_code=400, detail="Неверный режим: допустимы только 'cascade' или 'reassign'")

    await db.commit()

async def check_name(department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)) -> None:
    """
    Проверяет, что в пределах одного родителя нет подразделения с таким же именем.
    """
    if department.parent_id is not None:
        existing = await db.scalar(
            select(DepartmentModel)
            .where(DepartmentModel.parent_id == department.parent_id)
            .where(DepartmentModel.name == department.name)
        )
        if existing:
            raise HTTPException(status_code=400, detail="Подразделение с таким именем уже существует в указанном родителе")