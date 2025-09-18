# Асинхронщина и потоки (простой вариант)

Задания:
1. `delayed_print(message, delay)` — ждет и печатает.
2. `gather_three_messages()` — запускает сразу три `delayed_print` (2, 1, 3 сек) и возвращает порядок завершения.
3. Сравнение HTTP запросов:
    - `fetch_sync(urls)` — по очереди через `requests`
    - `fetch_async(urls)` — параллельно через `httpx.AsyncClient`
4. Потоки:
    - `print_message`, `run_prints_sequential`, `run_prints_threads`
      5–6. Гонка данных и решение с `threading.Lock`:
    - `run_race(num_threads, n_times, use_lock=False/True)`

## Как запустить тесты

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -U pip
pip install pytest pytest-asyncio httpx requests
pytest -q
