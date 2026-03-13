from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db_depends import get_async_db
from models.department import Department as DepartmentModel

async def collect_sub_departments(parent_id: int, current_depth: int, db: AsyncSession = Depends(get_async_db)):

        result = await db.scalars(select(DepartmentModel).where(DepartmentModel.parent_id == parent_id))
        sub_deps = result.all()
        
        all_sub_deps = []
        for dep in sub_deps:
            all_sub_deps.append(dep)
            if current_depth > 1:
                children = await collect_sub_departments(dep.id, current_depth - 1)
                all_sub_deps.extend(children)
        
        return all_sub_deps