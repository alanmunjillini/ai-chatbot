from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from app.core.security import create_access_token

router = APIRouter()

class LoginRequest(BaseModel):
    username: str


@router.post("/login")
def login(req: LoginRequest):
    user_id = str(uuid.uuid4())

    token = create_access_token(user_id)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user_id
    }