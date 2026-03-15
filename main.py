from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from routers import department, employee
from logger_config import setup_logging_middleware  # Импортируем настройку логера

app = FastAPI(title='FastAPI hitalent', version='0.1.0')

setup_logging_middleware(app)

app.include_router(department.router)
app.include_router(employee.router)

@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API"}
