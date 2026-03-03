import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

BASE_URL = "http://34.7.86.236:8000/v1"
API_KEY = "alanmunj"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

CONCURRENCY = 8     
REQUESTS = 50       
MAX_TOKENS = 128
PROMPT = "Explain transformers in simple terms."

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

def send_request():
    start = time.time()
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
        max_tokens=MAX_TOKENS,
    )
    latency = time.time() - start

    tokens = response.usage.total_tokens if response.usage else MAX_TOKENS
    return latency, tokens

def main():
    print(f"Starting load test:")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Total Requests: {REQUESTS}")
    print("--------------------------------------------------")

    start_time = time.time()
    latencies = []
    total_tokens = 0

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = [executor.submit(send_request) for _ in range(REQUESTS)]

        for future in as_completed(futures):
            latency, tokens = future.result()
            latencies.append(latency)
            total_tokens += tokens

    total_time = time.time() - start_time

    avg_latency = sum(latencies) / len(latencies)
    qps = REQUESTS / total_time
    tokens_per_sec = total_tokens / total_time

    print("--------------------------------------------------")
    print(f"Total time: {total_time:.2f} sec")
    print(f"Average latency: {avg_latency:.3f} sec")
    print(f"QPS: {qps:.2f}")
    print(f"Tokens/sec: {tokens_per_sec:.2f}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()