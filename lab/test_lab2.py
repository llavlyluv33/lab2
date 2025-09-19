import pytest
import asyncio
import time
import requests
import httpx

import lab2

@pytest.mark.asyncio
async def test_delayed_print_returns_message():
    msg = "hello"
    result = await lab2.delayed_print(msg, 0.1)
    assert result == msg

# ==== Задание 2 ====
@pytest.mark.asyncio
async def test_gather_three_messages_order_and_content():
    results = await lab2.gather_three_messages()
    assert set(results) == {"msg after 1s", "msg after 2s", "msg after 3s"}
    assert results[0] == "msg after 1s"


def test_fetch_sync_returns_order_and_times(monkeypatch):

    class DummyResponse:
        status_code = 200

    def fake_get(url, timeout=10.0):
        return DummyResponse()

    monkeypatch.setattr("requests.get", fake_get)

    urls = ["u1", "u2", "u3"]
    order, times, total = lab2.fetch_sync(urls)
    assert order == urls
    assert len(times) == len(urls)
    assert total >= 0

@pytest.mark.asyncio
async def test_fetch_async_returns_order_and_times(monkeypatch):
    class DummyResponse:
        status_code = 200

    class DummyClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, *args):
            return False
        async def get(self, url, timeout=10.0):
            await asyncio.sleep(0.01)
            return DummyResponse()

    monkeypatch.setattr("httpx.AsyncClient", lambda: DummyClient())

    urls = ["a", "b", "c"]
    order, times, total = await lab2.fetch_async(urls)
    assert set(order) == set(urls)
    assert set(times.keys()) == set(urls)
    assert total >= 0


def test_run_prints_sequential_and_threads():
    messages = ["x", "y", "z"]
    t_seq = lab2.run_prints_sequential(messages, 0.05)
    t_thr = lab2.run_prints_threads(messages, 0.05)

    assert t_thr < t_seq


def test_run_race_without_and_with_lock():
    num_threads = 10
    n_times = 1000

    val_without_lock = lab2.run_race(num_threads, n_times, use_lock=False)
    val_with_lock = lab2.run_race(num_threads, n_times, use_lock=True)


    assert val_with_lock == num_threads * n_times
    assert val_without_lock <= num_threads * n_times
