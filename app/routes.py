from fastapi import APIRouter
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
import json
import logging
import time

from .redis_client import redis_client
from .llm_client import client
from .metrics import (
    REQUEST_COUNT,
    REQUEST_ERRORS,
    REQUEST_LATENCY,
    IN_PROGRESS,
)

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    user_id: str = "demo_user"


# Metrics Endpoint
@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Chat Endpoint 
@router.post("/chat")
async def chat(req: ChatRequest):

    endpoint_name = "chat"

    REQUEST_COUNT.labels(endpoint=endpoint_name).inc()
    IN_PROGRESS.labels(endpoint=endpoint_name).inc()

    start_time = time.time()

    key = f"chat:{req.user_id}"
    lock_key = f"lock:{req.user_id}"

    # Acquire per-user lock
    acquired = redis_client.set(lock_key, "1", nx=True, ex=60)

    if not acquired:
        IN_PROGRESS.labels(endpoint=endpoint_name).dec()
        return {"error": "Another request is already in progress for this user"}

    try:
        # Read session history
        history_raw = redis_client.lrange(key, 0, -1)
        history = [json.loads(item) for item in history_raw]

        messages = (
            [{"role": "system", "content": "Respond clearly in English only."}]
            + history
            + [{"role": "user", "content": req.message}]
        )

        # Create LLM response 
        try:
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=messages,
                max_tokens=128,
                temperature=0.3,
                stream=True,
            )
        except Exception as e:
            REQUEST_ERRORS.labels(endpoint=endpoint_name).inc()
            return {"error": str(e)}

        # Streaming generator
        def stream_generator():
            full_response = ""

            try:
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield content

                # Append to Redis
                redis_client.rpush(
                    key, json.dumps({"role": "user", "content": req.message})
                )
                redis_client.rpush(
                    key,
                    json.dumps(
                        {"role": "assistant", "content": full_response}
                    ),
                )

                # Keep only last 20 messages
                redis_client.ltrim(key, -20, -1)

            except Exception:
                REQUEST_ERRORS.labels(endpoint=endpoint_name).inc()
                raise

        return StreamingResponse(stream_generator(), media_type="text/plain")

    finally:
        # Release lock + metrics
        redis_client.delete(lock_key)

        duration = time.time() - start_time
        REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(duration)
        IN_PROGRESS.labels(endpoint=endpoint_name).dec()


# Health Endpoint
@router.get("/health")
def health_check():
    status = {"api": "ok"}

    try:
        redis_client.ping()
        status["redis"] = "ok"
    except Exception:
        status["redis"] = "down"

    try:
        client.models.list()
        status["llm"] = "ok"
    except Exception:
        status["llm"] = "down"

    overall_status = "ok" if all(v == "ok" for v in status.values()) else "degraded"

    return {
        "status": overall_status,
        "details": status,
    }