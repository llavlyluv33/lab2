import asyncio
import time
import builtins
import pytest

from lab import tasks

pytestmark = pytest.mark.timeout(10)  # чтобы тесты не зависали


# Задание 1
@pytest.mark.asyncio
async def test_delayed_print_basic(monkeypatch):
    printed = []
    monkeypatch.setattr(builtins, "print", lambda *a, **k: printed.append(a[0] if a else ""))

    t0 = time.perf_counter()
    msg = await tasks.delayed_print("hi", 0.05)
    dt = time.perf_counter() - t0

    assert msg == "hi"
    assert printed == ["hi"]
    assert dt >= 0.05


# Задание 2
@pytest.mark.asyncio
async def test_gather_three_messages(monkeypatch):
    async def fake(message, delay):
        await asyncio.sleep(delay)
        print(message)
        return message

    monkeypatch.setattr(tasks, "delayed_print", fake)

    res = await tasks.gather_three_messages()
    assert res == ["msg after 1s", "msg after 2s", "msg after 3s"]


# Задание 3
def test_fetch_sync_monkeypatched(monkeypatch):
    delays = {
        "https://slow.example": 0.05,
        "https://medium.example": 0.02,
        "https://fast.example": 0.005,
    }

    class Resp:
        def __init__(self, code=200):
            self.status_code = code

    def fake_get(url, timeout=10.0):
        time.sleep(delays[url])
        return Resp(200)

    import requests
    monkeypatch.setattr(requests, "get", fake_get)

    urls = list(delays.keys())
    order, per_times, total = tasks.fetch_sync(urls)

    assert order == urls
    for u, t in zip(urls, per_times):
        assert pytest.approx(t, rel=0.4, abs=0.02) == delays[u]
    assert total >= sum(delays.values()) - 0.01


@pytest.mark.asyncio
async def test_fetch_async_monkeypatched(monkeypatch):
    delays = {
        "https://slow.example": 0.05,
        "https://medium.example": 0.02,
        "https://fast.example": 0.005,
    }

    class DummyResp:
        def __init__(self, status_code=200):
            self.status_code = status_code

    class DummyClient:
        async def __aenter__(self): return self

        async def __aexit__(self, exc_type, exc, tb): return False

        async def get(self, url, timeout=10.0):
            await asyncio.sleep(delays[url])
            return DummyResp(200)

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", lambda *a, **k: DummyClient())

    urls = list(delays.keys())
    order, times, total = await tasks.fetch_async(urls)

    assert order == ["https://fast.example", "https://medium.example", "https://slow.example"]
    for u in urls:
        assert pytest.approx(times[u], rel=0.5, abs=0.02) == delays[u]
    assert total >= max(delays.values()) - 0.01


# Задание 4
def test_threads_vs_sequential(monkeypatch):
    monkeypatch.setattr(tasks, "print_message", lambda m, d: time.sleep(d))

    msgs = ["A", "B", "C"]
    delay = 0.02

    t_seq = tasks.run_prints_sequential(msgs, delay)
    t_thr = tasks.run_prints_threads(msgs, delay)

    assert t_seq >= delay * len(msgs) - 0.01
    assert t_thr <= delay + 0.05


# Задания 5–6
def test_race_and_lock():
    n_threads = 20
    n_times = 10_000
    correct = n_threads * n_times

    val_no_lock = tasks.run_race(n_threads, n_times, use_lock=False)
    assert val_no_lock < correct
    val_with_lock = tasks.run_race(n_threads, n_times, use_lock=True)
    assert val_with_lock == correct
