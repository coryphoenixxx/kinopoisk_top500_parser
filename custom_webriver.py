from pathlib import Path
from selenium import webdriver
import screeninfo
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from itertools import cycle


class WebDriver(webdriver.Chrome):
    settings = None
    proc_nums = None

    def __init__(self, profile, window_rect):
        self.profile = profile
        self.window_rect = window_rect
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument(f'--user-data-dir={profile}')
        # self.options.add_argument(f'--headless')
        self.service = Service(executable_path=ChromeDriverManager().install())
        super().__init__(service=self.service, options=self.options)

    def show(self):
        self.set_window_rect(*self.window_rect)

    @classmethod
    def generate_settings(cls, procs_num):
        cls.proc_nums = procs_num
        profile_dirs = cls.create_profile_dirs(procs_num)
        windows_rects = cls.calc_windows_rects(procs_num)
        cls.settings = cycle(zip(profile_dirs, windows_rects))

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

        if procs_num == 4:
            window_width, window_height = int(monitor.width) // 2, (int(monitor.height) - 20) // 2
            window_rects = [
                (0, 0, window_width, window_height),
                (window_width, 0, window_width, window_height),
                (0, window_height, window_width, window_height),
                (window_width, window_height, window_width, window_height)
            ]

            return window_rects

        if procs_num == 8:
            window_width, window_height = int(monitor.width) // 4, (int(monitor.height) - 20) // 2
            window_rects = [
                (0, 0, window_width, window_height),
                (window_width, 0, window_width, window_height),
                (window_width*2, 0, window_width, window_height),
                (window_width*3, 0, window_width, window_height),
                (0, window_height, window_width, window_height),
                (window_width, window_height, window_width, window_height),
                (window_width*2, window_height, window_width, window_height),
                (window_width*3, window_height, window_width, window_height)
            ]

            return window_rects
