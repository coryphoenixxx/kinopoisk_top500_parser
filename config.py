import os
from multiprocessing import Queue
from pathlib import Path

import screeninfo
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Config:
    def __init__(self):
        self.proc_nums = int(os.getenv('PROCESS_NUM'))
        self.service = Service(executable_path=ChromeDriverManager(path=r".\drivers").install())
        self._user_data_dirs = self._create_user_data_dirs()
        self._windows_rects = self._calc_windows_rects()
        self._presets_queue = self.presets_queue

    @property
    def presets_queue(self):
        presets = Queue()
        for preset in zip(self._user_data_dirs, self._windows_rects):
            presets.put(preset)
        return presets

    def _create_user_data_dirs(self):
        dirs = []
        for i in range(self.proc_nums):
            path = Path().resolve() / f'user_datas/user_data_{i + 1}'
            path.mkdir(parents=True, exist_ok=True)
            dirs.append(path)
        return dirs

    def _calc_windows_rects(self):
        monitor = screeninfo.get_monitors()[0]

        if self.proc_nums == 2:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20)
            return [
                (0, 0, width, height),
                (width, 0, width, height),
            ]

        elif self.proc_nums == 4:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20) // 2
            return [
                (0, 0, width, height),
                (width, 0, width, height),
                (0, height, width, height),
                (width, height, width, height),
            ]

        elif self.proc_nums == 8:
            width, height = int(monitor.width) // 4, (int(monitor.height) - 20) // 2
            return [
                (0, 0, width, height),
                (width, 0, width, height),
                (width * 2, 0, width, height),
                (width * 3, 0, width, height),
                (0, height, width, height),
                (width, height, width, height),
                (width * 2, height, width, height),
                (width * 3, height, width, height),
            ]
        else:
            return None,


config = Config()
