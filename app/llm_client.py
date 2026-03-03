from openai import OpenAI
from httpx import Timeout
from .config import VLLM_BASE_URL, VLLM_API_KEY

client = OpenAI(
    base_url=VLLM_BASE_URL,
    api_key=VLLM_API_KEY,
    timeout=Timeout(30.0)
)