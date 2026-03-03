from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from httpx import Timeout
from openai import OpenAI
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
import json

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Slow down."},
    )

client = OpenAI(
    base_url="http://34.158.134.42:8000/v1", 
    api_key="alanmunj",
    timeout=Timeout(30.0)
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
@limiter.limit("3/minute")
async def chat(request: Request, req: ChatRequest):

    def stream_generator():
        try:
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": "Respond clearly in English only."},
                    {"role": "user", "content": req.message}
                ],
                max_tokens=256,
                temperature=0.3,
                stream=True,
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            print("Model error:", e)
            yield "\n\n Model unavailable. Please try again later."

    return StreamingResponse(stream_generator(), media_type="text/plain")

app.mount("/", StaticFiles(directory="static", html=True), name="static")