import redis

def test_redis_connection():
    r = redis.Redis(host="localhost", port=6379, decode_responses=True)

    r.set("hello", "world")
    value = r.get("hello")

    assert value == "world"