import asyncio
import time
import httpx

URL = "http://localhost:8000/chat"

TOTAL_REQUESTS = 50
CONCURRENCY = 8

async def send_request(client, i):
    payload = {
        "message": "Explain transformers in simple words"
    }
    start = time.time()
    response = await client.post(URL, json=payload)
    latency = time.time() - start
    return latency

async def main():
    limits = httpx.Limits(max_connections=CONCURRENCY)
    async with httpx.AsyncClient(limits=limits, timeout=60.0) as client:

        tasks = []
        for i in range(TOTAL_REQUESTS):
            tasks.append(send_request(client, i))

        start_time = time.time()
        latencies = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        print(f"Total time: {total_time:.2f} sec")
        print(f"Average latency: {sum(latencies)/len(latencies):.2f} sec")
        print(f"QPS: {TOTAL_REQUESTS/total_time:.2f}")

asyncio.run(main())