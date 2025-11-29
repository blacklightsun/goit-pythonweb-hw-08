from fastapi import FastAPI
from app.api.v1 import api_router  # Імпорт зібраного роутера
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Підключення всіх роутів однією строкою
app.include_router(api_router, prefix="/api/v1")
