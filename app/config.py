import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://34.158.134.42:8000/v1")
VLLM_API_KEY = os.getenv("VLLM_API_KEY", "alanmunj")