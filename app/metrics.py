from prometheus_client import Counter, Histogram, Gauge

# 总请求数
REQUEST_COUNT = Counter(
    "chat_requests_total",
    "Total number of chat requests",
    ["endpoint"]
)

# 错误数
REQUEST_ERRORS = Counter(
    "chat_request_errors_total",
    "Total number of failed chat requests",
    ["endpoint"]
)

# 延迟（秒）
REQUEST_LATENCY = Histogram(
    "chat_request_latency_seconds",
    "Latency of chat requests",
    ["endpoint"]
)

# 当前并发数
IN_PROGRESS = Gauge(
    "chat_requests_in_progress",
    "Number of chat requests currently being processed",
    ["endpoint"]
)