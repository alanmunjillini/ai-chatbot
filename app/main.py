from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI()

app.include_router(router)

app.mount("/", StaticFiles(directory="static", html=True), name="static")