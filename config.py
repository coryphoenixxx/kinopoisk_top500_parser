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
        self.movie_num = self.movie_list_num * 50
        self.still_num = int(os.getenv('STILLS_NUM'))
        self.scrape_limit_count = int(os.getenv('SCRAPE_LIMIT_COUNT'))
        self.scrape_limit_sleep = int(os.getenv('SCRAPE_LIMIT_SLEEP'))
        self.base_url = 'https://www.kinopoisk.ru'
        self.movie_lists_urls = [
            f"{self.base_url}/lists/movies/top500/?page={i + 1}"
            for i in range(self.movie_list_num)
        ]

        monitor = screeninfo.get_monitors()[0]
        self.m_width, self.m_height = int(monitor.width), int(monitor.height) - 30

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

        windows_rects = {
            2: self._calc_windows_rects(rows=1, columns=2),
            4: self._calc_windows_rects(rows=2, columns=2),
            6: self._calc_windows_rects(rows=2, columns=3),
            8: self._calc_windows_rects(rows=2, columns=4),
        }

        result = windows_rects.get(self.proc_num)
        if result:
            return result

        return (None,) * self.proc_num

    def _calc_windows_rects(self, rows, columns):
        w_w, w_h = self.m_width // columns, self.m_height // rows
        return [
            (w_w * i, w_h * j, w_w, w_h)
            for i in range(columns)
            for j in range(rows)
        ]


config = Config()
