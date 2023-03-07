import math
import time
from contextlib import suppress
from functools import wraps
from multiprocessing import Process, Manager
from typing import Collection, Optional

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

    with suppress(EOFError):
        while True:
            x = q.get()
            if x is None:
                break
            pbar.update(x)


def parallel_run(
        target: callable,
        tasks: Collection,
        result_type: Optional[type] = None,
        webdriver: bool = True,
        pbar_desc: Optional[str] = None,
        reduced: bool = False
):
    global_result = None
    if result_type:
        global_result = result_type()

    proc_num = config.proc_num if not reduced else math.ceil(config.proc_num / 2)

    args = []

    with Manager() as manager:
        task_queue = manager.Queue()
        for task in tasks:
            task_queue.put(task)
        args.append(task_queue)

        if result_type:
            if result_type is list:
                shared_result = manager.list()
            elif result_type is dict:
                shared_result = manager.dict()
            args.append(shared_result)

        if webdriver:
            args.append(config.presets)

        if pbar_desc:
            pbar_q = manager.Queue()
            pbar_proc = Process(target=_update_pbar, args=(pbar_q, len(tasks), pbar_desc), daemon=True)
            pbar_proc.start()
            args.append(pbar_q)

        processes = []
        for _ in range(proc_num):
            proc = Process(target=target, args=args)
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        if result_type is list:
            global_result.extend(shared_result)
        elif result_type is dict:
            global_result.update(shared_result)

        if pbar_desc:
            pbar_q.put(None)

    return global_result
