import os
from functools import cached_property
from multiprocessing import Queue

import screeninfo
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.file_manager import fm


class Config:
    def __init__(self):
        proc_num = os.getenv('PROCESS_NUM')
        self.proc_num = int(proc_num) if proc_num else os.cpu_count()
        self.service = Service(executable_path=ChromeDriverManager(path=r".\drivers").install())

    @property
    def presets(self):
        presets = Queue()
        for preset in zip(self._user_data_dirs, self._windows_rects):
            presets.put(preset)
        return presets

    @cached_property
    def _user_data_dirs(self):
        return [fm.user_data_i(i + 1).obj for i in range(self.proc_num)]

    @cached_property
    def _windows_rects(self):
        monitor = screeninfo.get_monitors()[0]

        if self.proc_num == 2:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20)
            return [
                (0, 0, width, height),
                (width, 0, width, height),
            ]

        elif self.proc_num == 4:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20) // 2
            return [
                (0, 0, width, height),
                (width, 0, width, height),
                (0, height, width, height),
                (width, height, width, height),
            ]

        elif self.proc_num == 6:
            width, height = int(monitor.width) // 3, (int(monitor.height) - 20) // 2
            return [
                (0, 0, width, height),
                (width, 0, width, height),
                (width * 2, 0, width, height),
                (0, height, width, height),
                (width, height, width, height),
                (width * 2, height, width, height),
            ]

        elif self.proc_num == 8:
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
