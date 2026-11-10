import time
import requests
from celery.utils.log import get_task_logger
from celery_app import app

logger = get_task_logger(__name__)

@app.task(bind=True, name="tasks.proses_event_uptime")
def proses_event_uptime(self, data):
    info = self.request.delivery_info or {}
    url = data.get("url", "https://httpbin.org/status/200")
    
    start = time.time()
    try:
        res = requests.get(url, timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        status = "ONLINE" if res.status_code == 200 else f"HTTP {res.status_code}"
    except Exception as e:
        latency = 0
        status = f"OFFLINE ({type(e).__name__})"

    logger.info(
        "[%s] Exchange=%r RoutingKey=%r | URL: %s -> Status: %s (%s ms)",
        self.request.hostname, info.get("exchange"), info.get("routing_key"), url, status, latency
    )
    return {"url": url, "status": status, "latency": latency}

# --- Task Pipeline (UTS Uptime Checker) ---
@app.task(name="tasks.ping_site")
def ping_site(url):
    try:
        res = requests.get(url, timeout=5)
        return {"url": url, "code": res.status_code}
    except Exception as e:
        return {"url": url, "code": 0, "error": str(e)}

@app.task(name="tasks.analisis_latency")
def analisis_latency(data):
    time.sleep(0.3)
    data["kategori"] = "NORMAL" if data["code"] == 200 else "ALERT/ERROR"
    return data