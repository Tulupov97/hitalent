from fastapi import FastAPI
from routers import department

app = FastAPI(title='FastAPI hitalent', version='0.1.0')

app.include_router(department.router)


@app.get("/")
async def root():
    """
    Корневой маршрут, подтверждающий, что API работает.
    """
    return {"message": "Добро пожаловать в API"}