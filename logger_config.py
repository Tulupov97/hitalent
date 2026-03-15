from fastapi.responses import JSONResponse
from loguru import logger
from uuid import uuid4

# Настройка логера
logger.add(
    "info.log",
    format="Log: [{extra[log_id]}:{time} - {level} - {message}]",
    level="INFO",
    enqueue=True
)

def get_request_logger():
    """Возвращает логер с контекстом log_id для конкретного запроса."""
    log_id = str(uuid4())
    return logger.bind(log_id=log_id)

def setup_logging_middleware(app):
    """Применяет middleware для логирования ко всем HTTP-запросам."""
    @app.middleware("http")
    async def log_middleware(request, call_next):
        log = get_request_logger()
        try:
            response = await call_next(request)
            if response.status_code in [401, 402, 403, 404]:
                log.warning(f"Запрос к {request.url.path} провален")
            else:
                log.info(f'Успешный доступ к {request.url.path}')
            return response
        except Exception as ex:
            log.error(f"Запрос к {request.url.path} провален: {ex}")
            return JSONResponse(content={"Успешно": False}, status_code=500)
