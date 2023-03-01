import time
from functools import wraps
from itertools import islice
from multiprocessing import Process, Manager
from pathlib import Path
from typing import Iterable

from config import config


def jsonkeystoint(x):
    return {int(k): v for k, v in x.items()}


def chunkize(it, size):
    it = iter(it)
    return iter(lambda: tuple(islice(it, size)), ())


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Function {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def run_in_parallel(
        target: callable,
        tasks: Iterable,
        get_result: bool = False,
        webdriver: bool = False
):
    global_result = []

    with Manager() as manager:
        args = []

        tasks_queue = manager.Queue()
        for task in tasks:
            tasks_queue.put(task)
        args.append(tasks_queue)

        if get_result:
            result = manager.list()
            args.append(result)

        if webdriver:
            args.append(config.presets)

        processes = []
        for _ in range(config.proc_nums):
            proc = Process(target=target, args=args)
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        if get_result:
            global_result.extend(result)

    return global_result


def get_file(filepath):
    file = Path().resolve() / filepath
    file.parent.mkdir(parents=True, exist_ok=True)
    return file
