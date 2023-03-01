import time
from functools import wraps
from multiprocessing import Process, Manager
from pathlib import Path
from typing import Iterable

from tqdm import tqdm

from config import config


def timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'\nFunction {func.__name__}{args} {kwargs} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def _update_pbar(q, total, desc):
    pbar = tqdm(desc=desc, total=total)

    while True:
        x = q.get()
        if x is None:
            break
        pbar.update(x)


def run_in_parallel(
        target: callable,
        tasks: Iterable,
        shared_result: bool = False,
        webdriver: bool = False,
        pbar_desc: str = None,
):
    global_result = []

    with Manager() as manager:
        args = []

        tasks_queue = manager.Queue()
        for task in tasks:
            tasks_queue.put(task)
        args.append(tasks_queue)

        if shared_result:
            result = manager.list()
            args.append(result)

        if webdriver:
            args.append(config.presets_queue)

        if pbar_desc:
            pbar_queue = manager.Queue()
            pbar_proc = Process(target=_update_pbar, args=(pbar_queue, len(tasks), pbar_desc), daemon=True)
            pbar_proc.start()
            args.append(pbar_queue)

        processes = []
        for _ in range(config.proc_nums):
            proc = Process(target=target, args=args)
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        if shared_result:
            global_result.extend(result)

        if pbar_desc:
            pbar_queue.put(None)

    return global_result


def get_file(filepath):
    file = Path().resolve() / filepath
    file.parent.mkdir(parents=True, exist_ok=True)
    return file
