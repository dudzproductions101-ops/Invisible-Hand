# stress.py

import time
import random
import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import logs

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "curl/8.0.1",
    "Wget/1.21.3"
]

METHODS_V2 = ["GET", "HEAD", "OPTIONS", "POST"]


def build_request_params_v2():
    method = random.choice(METHODS_V2)
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*",
        "Cache-Control": "no-cache",
        "Accept-Language": random.choice(["en-US", "en-GB", "pt-PT", "es-ES"]),
        "Connection": random.choice(["keep-alive", "close"]),
        "Referer": random.choice([
            "https://google.com",
            "https://github.com",
            "https://example.com",
            "https://invisible-hand.local"
        ])
    }
    cookies = {
        "session": str(random.randint(100000, 999999)),
        "mode": random.choice(["stress", "test", "debug"])
    }
    payload = {
        "data": str(random.randint(0, 999999)),
        "flag": random.choice(["A", "B", "C", "D"])
    }
    return method, headers, cookies, payload


def worker(session, url, delay, smart, stats, stop_event, pause_event, name: str):
    while not stop_event.is_set():
        while pause_event.is_set():
            time.sleep(0.01)
        start = time.time()
        try:
            if smart:
                method, headers, cookies, payload = build_request_params_v2()
            else:
                method, headers, cookies, payload = "GET", {}, {}, {}
            if method == "GET":
                response = session.get(url, headers=headers, cookies=cookies, timeout=10)
            elif method == "HEAD":
                response = session.head(url, headers=headers, cookies=cookies, timeout=10)
            elif method == "OPTIONS":
                response = session.options(url, headers=headers, cookies=cookies, timeout=10)
            else:
                response = session.post(url, headers=headers, cookies=cookies, data=payload, timeout=10)
            elapsed = time.time() - start
            code = response.status_code
            stats["total"] += 1
            stats["codes"][code] = stats["codes"].get(code, 0) + 1
            stats["times"].append(elapsed)
            stats["fastest"] = min(stats["fastest"], elapsed)
            stats["slowest"] = max(stats["slowest"], elapsed)
            logs.log(f"[{name}] {method} → {code} ({elapsed:.3f}s)")
        except requests.exceptions.Timeout:
            elapsed = time.time() - start
            stats["total"] += 1
            stats["errors"] += 1
            stats["timeouts"] += 1
            stats["times"].append(elapsed)
            logs.log(f"[{name}] TIMEOUT")
        except Exception as e:
            elapsed = time.time() - start
            stats["total"] += 1
            stats["errors"] += 1
            stats["times"].append(elapsed)
            logs.log(f"[{name}] ERROR → {e}", level="error")
        if delay > 0:
            time.sleep(delay)


def run_stress(url, num_threads, delay, smart, stats, stop_event, pause_event):
    threads = []
    for i in range(num_threads):
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        name = f"Worker-{i+1}"
        t = threading.Thread(
            target=worker,
            args=(session, url, delay, smart, stats, stop_event, pause_event, name),
            name=name
        )
        threads.append(t)
        t.start()
    return threads
