from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from .redis_client import redis_client
from .llm_client import client

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "demo_user"

@router.post("/chat")
async def chat(req: ChatRequest):

    def stream_generator():
        key = f"chat:{req.user_id}"

        history_raw = redis_client.lrange(key, 0, -1)
        history = [json.loads(item) for item in history_raw]

        messages = (
            [{"role": "system", "content": "Respond clearly in English only."}]
            + history
            + [{"role": "user", "content": req.message}]
        )

        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            messages=messages,
            max_tokens=128,
            temperature=0.3,
            stream=True,
        )

        full_response = ""

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content

        redis_client.rpush(key, json.dumps({"role": "user", "content": req.message}))
        redis_client.rpush(key, json.dumps({"role": "assistant", "content": full_response}))
        redis_client.ltrim(key, -20, -1)

    return StreamingResponse(stream_generator(), media_type="text/plain")