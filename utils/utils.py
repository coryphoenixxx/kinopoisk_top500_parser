import time
from contextlib import suppress
from functools import wraps
from multiprocessing import Process, Manager, Value
from typing import Collection, Optional

from prettytable import PrettyTable
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
        print(f'\n{func.__name__}{args} {kwargs} ——— {total_time:.4f} сек.')
        return result

    return timeit_wrapper


def _chunked(lst, n):
    for i in range(0, len(lst), n):
        x = lst[i:i + n]
        x.extend([''] * (n - len(x)))
        yield x


def show_persons_countries():
    if file_m.persons_data_json.exists():
        persons_data = file_m.persons_data_json.read()

        countries = set()
        for data in persons_data:
            motherland = data['motherland']
            if motherland:
                countries.add(motherland)

        table = PrettyTable()
        for chunk in _chunked(sorted(countries), n=6):
            table.add_row(chunk)

        print(table)

    else:
        print("Отсутствует файл data/persons_data.json!")


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
        counter: bool = False,
        pbar_desc: Optional[str] = None,
):
    run_result = []
    proc_num = min(config.proc_num, len(tasks))
    args = []

    with Manager() as manager:
        task_queue = manager.Queue()
        for task in tasks:
            task_queue.put(task)
        args.append(task_queue)

        result = manager.list()
        args.append(result)

        if counter:
            counter = Value('i', 0)
            args.append(counter)

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

        run_result.extend(result)

        if pbar_desc:
            pbar_q.put(None)

    return run_result
