from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

app = FastAPI()

client = OpenAI(
    base_url="http://10.164.0.2:8000/v1",
    api_key="alanmunj"
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    response = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": req.message}],
        max_tokens=128,
    )

    return {"reply": response.choices[0].message.content}

app.mount("/", StaticFiles(directory="static", html=True), name="static")
