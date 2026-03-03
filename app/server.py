from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from httpx import Timeout
from openai import OpenAI
import json

app = FastAPI()

client = OpenAI(
    base_url="http://34.158.134.42:8000/v1", 
    api_key="alanmunj",
    timeout=Timeout(30.0)
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):

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