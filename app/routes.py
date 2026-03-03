from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
from .redis_client import redis_client
from .llm_client import client
import logging
import time
from .metrics import (
    REQUEST_COUNT,
    REQUEST_ERRORS,
    REQUEST_LATENCY,
    IN_PROGRESS,
)
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str = "demo_user"

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@router.post("/chat")
async def chat(req: ChatRequest):

    endpoint_name = "chat"

    REQUEST_COUNT.labels(endpoint=endpoint_name).inc()
    IN_PROGRESS.labels(endpoint=endpoint_name).inc()

    start_time = time.time()

    def stream_generator():
        try:
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

        except Exception:
            REQUEST_ERRORS.labels(endpoint=endpoint_name).inc()
            raise
        finally:
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(duration)
            IN_PROGRESS.labels(endpoint=endpoint_name).dec()

    return StreamingResponse(stream_generator(), media_type="text/plain")


@router.get("/health")
def health_check():
    status = {"api": "ok"}

    # Check Redis
    try:
        redis_client.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "down"

    # Check LLM backend
    try:
        client.models.list()  
        status["llm"] = "ok"
    except Exception:
        status["llm"] = "down"

    overall_status = "ok" if all(v == "ok" for v in status.values()) else "degraded"

    return {
        "status": overall_status,
        "details": status
    }