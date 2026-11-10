import argparse
import time
from celery import chain
from celery_app import app, FANOUT_QUEUES, TOPIC_QUEUES, WILDCARD_QUEUES

SITES = [
    "https://google.com",
    "https://github.com",
    "https://httpstat.us/500",
    "https://domain-invalid-12345.com"
]

def demo_fanout(count):
    for i in range(count):
        payload = {"id": i, "url": SITES[i % len(SITES)]}
        app.send_task("tasks.proses_event_uptime", args=[payload],
                      exchange="uptime.broadcast", routing_key="",
                      declare=FANOUT_QUEUES)
        print(f"[Fan-Out] Pesan #{i} disiarkan ke semua queue")
        time.sleep(0.3)

def demo_topic(count):
    keys = ["check.http.single", "check.db.single"]
    for i in range(count):
        key = keys[i % len(keys)]
        payload = {"id": i, "url": SITES[i % len(SITES)]}
        app.send_task("tasks.proses_event_uptime", args=[payload],
                      exchange="uptime.topic", routing_key=key,
                      declare=TOPIC_QUEUES)
        print(f"[Topic] Pesan #{i} sent dengan key: {key}")
        time.sleep(0.3)

def demo_wildcard(count):
    keys = ["check.http.api", "alert.critical.server_down", "check.db.single"]
    for i in range(count):
        key = keys[i % len(keys)]
        payload = {"id": i, "url": SITES[i % len(SITES)]}
        app.send_task("tasks.proses_event_uptime", args=[payload],
                      exchange="uptime.topic", routing_key=key,
                      declare=TOPIC_QUEUES + WILDCARD_QUEUES)
        print(f"[Wildcard] Pesan #{i} sent dengan key: {key}")
        time.sleep(0.3)

def demo_pipeline():
    res = chain(
        app.signature("tasks.ping_site", args=["https://google.com"]),
        app.signature("tasks.analisis_latency")
    ).apply_async()
    print("[Pipeline UTS] Menunggu hasil dari worker...")
    print("[Pipeline UTS] Hasil:", res.get(timeout=30))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fanout", "topic", "wildcard", "pipeline"])
    parser.add_argument("--count", type=int, default=4)
    args = parser.parse_args()

    if args.mode == "fanout":
        demo_fanout(args.count)
    elif args.mode == "topic":
        demo_topic(args.count)
    elif args.mode == "wildcard":
        demo_wildcard(args.count)
    elif args.mode == "pipeline":
        demo_pipeline()