import os
from functools import cached_property
from multiprocessing import Queue

import screeninfo
from dotenv import load_dotenv

from utils.file_manager import storage

load_dotenv()


class Config:
    def __init__(self):
        proc_num = os.getenv('PROCESS_NUM')
        self.proc_num = int(proc_num) if proc_num else os.cpu_count()
        self.movie_list_num = int(os.getenv('MOVIES_LIST_NUM'))
        self.monitor = sorted(screeninfo.get_monitors(), key=lambda m: m.x)[int(os.getenv('MONITOR'))]
        self.movie_num = self.movie_list_num * 50
        self.still_num = int(os.getenv('STILLS_NUM'))
        self.scrape_limit_count = int(os.getenv('SCRAPE_LIMIT_COUNT'))
        self.scrape_limit_sleep = int(os.getenv('SCRAPE_LIMIT_SLEEP'))
        self.base_url = 'https://www.kinopoisk.ru'
        self.movie_lists_urls = [
            f"{self.base_url}/lists/movies/top500/?page={i + 1}"
            for i in range(self.movie_list_num)
        ]

    @property
    def presets(self):
        presets = Queue()
        for preset in zip(self._driver_dirs, self._user_data_dirs, self._windows_rects):
            presets.put(preset)
        return presets

    @cached_property
    def _driver_dirs(self):
        """Создание папки вебдрайвер под каждый процесс"""

        return [storage.driver_dir(i + 1).mkdir() for i in range(self.proc_num)]

    @cached_property
    def _user_data_dirs(self):
        """Создание папки профиля chrome под каждый процесс"""

        return [storage.user_data_dir(i + 1).mkdir() for i in range(self.proc_num)]

    @cached_property
    def _windows_rects(self):
        """Расчет позиции и размеров окна вебдрайвера под каждый процесс"""

        rows_columns = {
            2: (1, 2),
            4: (2, 2),
            6: (2, 3),
            8: (2, 4),
            16: (4, 4)
        }

        if self.proc_num in rows_columns.keys():
            return self._calc_windows_rects(*rows_columns[self.proc_num])
        return (None,) * self.proc_num

    def _calc_windows_rects(self, rows, columns):
        window_width, window_height = self.monitor.width // columns, self.monitor.height // rows
        return [
            (
                window_width * i + self.monitor.x,  # start pos_x
                window_height * j + self.monitor.y,  # start pos_y
                window_width,
                window_height
            )
            for i in range(columns)
            for j in range(rows)
        ]


config = Config()
