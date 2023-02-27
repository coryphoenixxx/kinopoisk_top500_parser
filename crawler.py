from multiprocessing import Semaphore, Process, Manager

from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver


class Crawler:
    def __init__(self):
        self.base_url = "https://www.kinopoisk.ru/"
        self.movie_list_urls = [f"{self.base_url}/lists/movies/top500/?page={i + 1}" for i in range(10)]

    def run(self):
        return self._get_movie_urls()

    def _get_movie_urls(self):
        return self._run_in_parallel(
            target=self._get_movie_urls_job,
            urls=self.movie_list_urls
        )

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

        return dict(sorted(global_result.items()))
