from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import Department as DepartmentSchema, DepartmentCreate
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from db_depends import get_async_db

router = APIRouter(prefix='/departments', tags=['departments'])

@router.post('/', response_model=DepartmentSchema, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новое подразделение.
    """
    return {'message': 'True'}