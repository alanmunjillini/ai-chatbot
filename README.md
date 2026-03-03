# AI Chatbot Backend (Stateful LLM Service)

A stateful LLM backend built with FastAPI, Redis, and vLLM.

This project demonstrates how to build a production-style AI microservice with session memory, streaming responses, observability, and metrics.

---

## Architecture

Client  
↓  
FastAPI (async API layer)  
↓  
Redis (session memory)  
↓  
vLLM OpenAI-compatible API (GPU inference)

---

## Implemented Features

### 1. Stateful Multi-Turn Chat
- Redis-backed session memory
- History stored per `user_id`
- Bounded memory (last 20 messages)

### 2. Streaming Responses
- Token streaming from vLLM
- End-to-end async processing

### 3. Multi-User Support
- Redis key: `chat:{user_id}`
- User sessions isolated

### 4. Observability
- Structured logging
- Request latency logging
- Error logging

### 5. Health Check
Endpoint: `/health`
- Checks API
- Checks Redis connectivity
- Checks vLLM backend

### 6. Metrics (Prometheus)
Endpoint: `/metrics`

Exposed metrics:
- `chat_requests_total`
- `chat_request_errors_total`
- `chat_request_latency_seconds`
- `chat_requests_in_progress`

Enables:
- QPS calculation
- Average latency
- Error rate
- Concurrency tracking

---

## Tech Stack

- Python 3.12
- FastAPI (async API)
- Redis (session store)
- vLLM (GPU inference backend)
- Prometheus Client (metrics)
- Docker (Redis local dev)

---
## Setup

### 1. Install Dependencies
pip install -r requirements.txt


### 2. Run Redis (Local)
docker run -d
--name redis-dev
-p 6379:6379
redis
redis-server --save "" --appendonly no

### 3. Start Server
uvicorn app.main:app --reload

Server runs at:
http://localhost:8000
