from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.logging_config import setup_logging
from app.api.auth import router as auth_router

setup_logging()

app = FastAPI()

app.include_router(auth_router)

app.include_router(router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def chat_page():
    return FileResponse("static/chat.html")

@app.get("/intro")
def intro_page():
    return FileResponse("static/intro.html")