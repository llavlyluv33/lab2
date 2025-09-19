import asyncio
import time
import threading

#1
async def delayed_print(message: str, delay: float) -> str:
    await asyncio.sleep(delay)
    print(message)
    return message


#2
async def gather_three_messages():
    results = await asyncio.gather(
        delayed_print("message 2 задержка 1 сек", 1),
        delayed_print("message 1 задержка 2 сек", 2),
        delayed_print("message 3 задержка 3 сек", 3)
    )

    print(f"Результаты: {results}")
    return results


#4
def print_message(message: str, delay: float):
    time.sleep(delay)
    print(message)


def run_prints_sequential(messages: str, delay: float):
    start_time = time.time()
    for m in messages:
        print_message(m, delay)
    return time.time() - start_time


def run_prints_threads(messages: str, delay: float):
    start_time = time.time()
    threads = [threading.Thread(target=print_message, args=(m, delay)) for m in messages]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return time.time() - start_time


#5-6
counter = 0
lock = threading.Lock()


def increment_without_lock(iterations: int = 1000):
    global counter
    for _ in range(iterations):
        current_value = counter
        current_value += 1
        counter = current_value


def increment_with_lock(iterations: int = 1000):
    global counter
    for _ in range(iterations):
        with lock:
            current_value = counter
            current_value += 1
            counter = current_value


def run_race(iterations: int = 1000, use_lock: bool = False):
    global counter
    counter = 0
    target = increment_with_lock if use_lock else increment_without_lock

    threads = [threading.Thread(target=target, args=(iterations,)) for _ in range(10)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()

    return counter
