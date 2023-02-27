import json
from multiprocessing import Semaphore, Process, Manager
from pathlib import Path

from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from utils import jsonkeystoint


class Crawler:
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru/"
        self.movie_list_urls = [f"{self.base_url}/lists/movies/top500/?page={i + 1}" for i in range(10)]
        self.movie_urls = None

    def run(self):
        return self._get_movie_urls()

    def _get_movie_urls(self):
        file = Path().resolve() / 'data/movie_list_urls.json'
        file.parent.mkdir(parents=True, exist_ok=True)

        if file.exists():
            with file.open(mode='r', encoding='utf-8') as f:
                result = json.load(f, object_hook=jsonkeystoint)
        else:
            result = self._run_in_parallel(
                target=self._get_movie_urls_job,
                urls=self.movie_list_urls
            )

            with file.open(mode='w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=4)

        self.movie_urls = result
        return self.movie_urls

    @staticmethod
    def _get_movie_urls_job(url, presets, semaphore, result: dict):
        with semaphore:
            with WebDriver(url=url, presets=presets) as driver:
                movie_blocks = driver.find_elements(By.CSS_SELECTOR, ".styles_root__ti07r")

                d = {}
                for block in movie_blocks:
                    position = block.find_element(By.CSS_SELECTOR, ".styles_position__TDe4E") \
                        .text
                    url = block.find_element(By.CSS_SELECTOR, ".base-movie-main-info_link__YwtP1") \
                        .get_attribute('href')

                    d[int(position)] = url

                result.update(d)

    @staticmethod
    def _run_in_parallel(target, urls):
        global_result = {}
        presets = config.presets
        semaphore = Semaphore(config.proc_nums)

        with Manager() as manager:
            result = manager.dict()
            processes = []

            for url in urls:
                proc = Process(target=target, args=(url, presets, semaphore, result))
                processes.append(proc)
                proc.start()

            for proc in processes:
                proc.join()

            global_result.update(result)

        return global_result
