import os
from celery import Celery
from kombu import Exchange, Queue

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

app = Celery("uptime_checker", broker=BROKER_URL, backend=RESULT_BACKEND, include=["tasks"])

# --- Exchanges ---
default_ex = Exchange("default", type="direct")
fanout_ex = Exchange("uptime.broadcast", type="fanout")
topic_ex = Exchange("uptime.topic", type="topic")

# --- Queues ---
FANOUT_QUEUES = [
    Queue("fanout.log_system", fanout_ex),
    Queue("fanout.notif_telegram", fanout_ex),
]

TOPIC_QUEUES = [
    Queue("topic.http_check", topic_ex, routing_key="check.http.single"),
    Queue("topic.db_check", topic_ex, routing_key="check.db.single"),
]

WILDCARD_QUEUES = [
    Queue("wild.all_http", topic_ex, routing_key="check.http.*"),
    Queue("wild.critical_alerts", topic_ex, routing_key="alert.#"),
]

app.conf.task_queues = tuple(
    [Queue("default", default_ex, routing_key="default")]
    + FANOUT_QUEUES + TOPIC_QUEUES + WILDCARD_QUEUES
)

app.conf.task_default_queue = "default"
app.conf.task_default_exchange = "default"
app.conf.task_default_routing_key = "default"

app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Jakarta",
    enable_utc=True,
    worker_prefetch_multiplier=1,
)