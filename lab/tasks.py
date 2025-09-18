import asyncio
import time
import threading

# Задание 1
async def delayed_print(message: str, delay: float) -> str:
    await asyncio.sleep(delay)
    print(message)
    return message


# Задание 2
async def gather_three_messages():
    t1 = asyncio.create_task(delayed_print("msg after 2s", 2))
    t2 = asyncio.create_task(delayed_print("msg after 1s", 1))
    t3 = asyncio.create_task(delayed_print("msg after 3s", 3))

    results = []
    for coro in asyncio.as_completed([t1, t2, t3]):
        res = await coro
        results.append(res)

    return results

# Задание 3 (HTTP-запросы)
def fetch_sync(urls, timeout=10.0):
    import requests

    order = []
    per_url_times = []
    t0 = time.perf_counter()

    for url in urls:
        start = time.perf_counter()
        try:
            r = requests.get(url, timeout=timeout)
            _ = r.status_code
        except Exception:
            pass
        per_url_times.append(time.perf_counter() - start)
        order.append(url)

    total = time.perf_counter() - t0
    return order, per_url_times, total


async def fetch_async(urls, timeout=10.0):
    import httpx

    async def one(client, url):
        start = time.perf_counter()
        try:
            r = await client.get(url, timeout=timeout)
            _ = r.status_code
        except Exception:
            pass
        return url, time.perf_counter() - start

    t0 = time.perf_counter()
    async with httpx.AsyncClient() as client:
        tasks = [asyncio.create_task(one(client, u)) for u in urls]
        completion_order = []
        times = {}
        for coro in asyncio.as_completed(tasks):
            url, dt = await coro
            completion_order.append(url)
            times[url] = dt
    total = time.perf_counter() - t0
    return completion_order, times, total


# Задание 4
def print_message(message: str, delay: float):
    time.sleep(delay)
    print(message)


def run_prints_sequential(messages, delay: float):
    t0 = time.perf_counter()
    for m in messages:
        print_message(m, delay)
    return time.perf_counter() - t0


def run_prints_threads(messages, delay: float):
    t0 = time.perf_counter()
    ths = [threading.Thread(target=print_message, args=(m, delay)) for m in messages]
    for th in ths:
        th.start()
    for th in ths:
        th.join()
    return time.perf_counter() - t0


# Задания 5–6
_counter = 0
_lock = threading.Lock()


def reset_counter():
    global _counter
    _counter = 0


def increment_without_lock(n_times: int, step: int = 1):
    global _counter
    for _ in range(n_times):
        cur = _counter
        cur += step
        _counter = cur


def increment_with_lock(n_times: int, step: int = 1):
    global _counter
    for _ in range(n_times):
        with _lock:
            _counter += step


def run_race(num_threads: int, n_times: int, use_lock: bool = False):
    reset_counter()
    target = increment_with_lock if use_lock else increment_without_lock

    ths = [threading.Thread(target=target, args=(n_times,)) for _ in range(num_threads)]
    for th in ths:
        th.start()
    for th in ths:
        th.join()

    return _counter
