import math
import time
from collections import defaultdict
from contextlib import suppress
from functools import wraps
from multiprocessing import Process, Manager
from typing import Collection, Optional

from tabulate import tabulate
from tqdm import tqdm

from config import config
from utils.file_manager import file_m


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


def show_persons_countries():
    if file_m.persons_data_json.exists():
        persons_data = file_m.persons_data_json.read()

        countries_count = defaultdict(int)
        for data in persons_data:
            countries_count[data['motherland']] += 1

        table = [['Страна', 'Количество'], ]
        for t in sorted(countries_count.items(), key=lambda x: x[1], reverse=True):
            table.append(t)

        print(tabulate(table, headers='firstrow', tablefmt='fancy_grid'))
    else:
        print("Отсутствует файл persons_data.json!")


def _update_pbar(q, total, desc):
    pbar = tqdm(desc=desc, total=total)
    with suppress(EOFError):
        while True:
            x = q.get()
            if x is None:
                break
            pbar.update(1)


def parallel_run(
        target: callable,
        tasks: Collection,
        result_type: Optional[type] = None,
        webdriver: bool = True,
        pbar_desc: Optional[str] = None,
        reduced: bool = False
):
    run_result = None
    if result_type:
        run_result = result_type()

    proc_num = config.proc_num if not reduced else math.ceil(config.proc_num / 2)
    tasks_num = len(tasks)
    if tasks_num < proc_num:
        proc_num = tasks_num

    args = []

    with Manager() as manager:
        task_queue = manager.Queue()
        for task in tasks:
            task_queue.put(task)
        args.append(task_queue)

        if result_type:
            if result_type is list:
                shared_data = manager.list()
            elif result_type is dict:
                shared_data = manager.dict()
            args.append(shared_data)

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
            run_result.extend(shared_data)
        elif result_type is dict:
            run_result.update(shared_data)

        if pbar_desc:
            pbar_q.put(None)

    return run_result
