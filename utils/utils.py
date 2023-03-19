import time
from contextlib import suppress
from functools import wraps
from itertools import zip_longest
from multiprocessing import Process, Manager, Value, Queue
from typing import Collection

from prettytable import PrettyTable
from tqdm import tqdm

from config import config
from models import Person
from utils.file_manager import storage


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


def _chunkize(lst, n):
    for i in range(0, len(lst), n):
        sub_lst = lst[i:i + n]
        yield sub_lst


def show_countries():
    """Вывод стран для дальнейшей ручной доработки"""

    if storage.persons_data_json.exists():
        persons = storage.persons_data_json.read(Person)

        countries = set(person.motherland for person in persons)
        countries.remove(None)

        table = PrettyTable()
        table.header = False
        table.title = 'СТРАНЫ'

        countries_chunks = map(list, zip_longest(*_chunkize(sorted(countries), n=20), fillvalue=''))
        for chunk in countries_chunks:
            table.add_row(chunk)
        print(table)
    else:
        print("Отсутствует файл data/persons_data.json!")


def _update_pbar(q: Queue, total: int, desc: str):
    """Обновление полоски прогресс-бара"""

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
        pbar_desc: str,
        counter: bool = False,
) -> list:
    """
    :param target: Объект функции для параллельного выполнения
    :param tasks: Список задач для target
    :param counter: Нужен ли расшаренный между процессами счетчик
    :param pbar_desc: Описание прогресс-бара
    :return: Список с результатами работы всех процессов
    """

    proc_num = min(config.proc_num, len(tasks))

    with Manager() as manager:
        task_q = manager.Queue()
        for task in tasks:
            task_q.put(task)

        result = manager.list()

        # Создать демон прогресс-бара
        pbar_q = manager.Queue()
        pbar_proc = Process(
            target=_update_pbar,
            args=(pbar_q, len(tasks), pbar_desc),
            daemon=True,
        )
        pbar_proc.start()

        # порядок важен!
        args = []
        args.extend([
            task_q,
            result,
            config.presets,
            pbar_q,
        ])
        if counter:
            args.append(Value('i', 0))

        # Создать процессы-воркеры вебдрайверов
        processes = []
        for _ in range(proc_num):
            proc = Process(target=target, args=args)
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        pbar_q.put(None)

        return list(result)
