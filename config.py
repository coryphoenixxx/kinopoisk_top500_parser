import os
from itertools import cycle
from pathlib import Path

import screeninfo
from dotenv import load_dotenv

load_dotenv()


class Config:
    presets = None
    proc_nums = int(os.getenv('PROCESS_NUM'))

    def __init__(self):
        self.generate()

    @classmethod
    def generate(cls):
        profile_dirs = cls.create_profile_dirs(cls.proc_nums)
        windows_rects = cls.calc_windows_rects(cls.proc_nums)
        cls.presets = cycle(zip(profile_dirs, windows_rects))

    @classmethod
    def create_profile_dirs(cls, procs_num):
        dirs = []
        for i in range(procs_num):
            path = Path().resolve() / f'profiles/profile_{i}'
            path.mkdir(parents=True, exist_ok=True)
            dirs.append(path)
        return dirs

    @classmethod
    def calc_windows_rects(cls, procs_num):
        monitor = screeninfo.get_monitors()[0]

        if procs_num == 2:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20)
            return [
                (0, 0, width, height),
                (width, 0, width, height),
            ]

        elif procs_num == 4:
            width, height = int(monitor.width) // 2, (int(monitor.height) - 20) // 2
            return [
                (0, 0, width, height),
                (width, 0, width, height),
                (0, height, width, height),
                (width, height, width, height),
            ]

        elif procs_num == 8:
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


config = Config()
