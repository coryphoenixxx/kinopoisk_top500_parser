import json
import time
from pathlib import Path

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from utils import run_in_parallel, get_file


class Scraper:
    def __init__(self):
        self.base_url = 'https://www.kinopoisk.ru'

    def solve_captchas(self):
        user_datas_dir = Path().resolve() / 'user_datas'
        profiles_not_exists = [not (user_data_dir / 'Default').exists() for user_data_dir in user_datas_dir.iterdir()]

        if all(profiles_not_exists):
            run_in_parallel(
                target=self._solve_capthas_job,
                tasks=[self.base_url] * config.proc_nums,
                webdriver=True,
                pbar_desc="Решение капчи",
            )
        else:
            print("Решение капчи не требуется...")

    def download_movie_list_pages(self):
        file = get_file(path='data/movie_urls.json')

        if not file.exists():
            movie_list_urls = [f"{self.base_url}/lists/movies/top500/?page={i + 1}" for i in range(10)]

            run_in_parallel(
                target=self._download_movie_list_pages_job,
                tasks=movie_list_urls,
                webdriver=True,
                pbar_desc="Скачивание страниц со списками фильмов",
            )
        else:
            print("Скачивание страниц со списками фильмов не требуется...")

    def download_movie_pages(self):
        file = get_file(path='data/movie_urls.json')

        with file.open(mode='r', encoding='utf-8') as f:
            json_dict: dict = json.load(f)

        movies_urls = [item.values() for item in json_dict['movies']][:50]

        run_in_parallel(
            target=self._download_movie_pages_job,
            tasks=movies_urls,
            webdriver=True,
            pbar_desc="Скачивание страниц фильмов",
        )

    @staticmethod
    def _solve_capthas_job(urls_queue, presets, pbar):
        url = urls_queue.get()
        with WebDriver(url=url, presets=presets, js=True) as driver:
            while 'showcaptcha' not in driver.current_url:
                time.sleep(0.5)
                driver.refresh()

            try:
                driver.find_element(By.CSS_SELECTOR, ".CheckboxCaptcha-Button").click()
            except NoSuchElementException:
                pass

            while 'showcaptcha' in driver.current_url:
                time.sleep(0.5)

            pbar.put_nowait(1)

    @staticmethod
    def _download_movie_list_pages_job(urls_queue, presets, pbar):
        while not urls_queue.empty():
            url = urls_queue.get()
            number = int(url.split('page=')[-1])

            file = get_file(path=f'data/pages/movie_lists/page_{number:02d}.html')

            with WebDriver(url=url, presets=presets, expected_selector='.styles_root__ti07r') as driver:
                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)

    @staticmethod
    def _download_movie_pages_job(urls_queue, presets, pbar):
        while not urls_queue.empty():
            number, url = urls_queue.get()

            file = get_file(path=f'data/pages/movies/movie_{number:03d}.html')

            with WebDriver(url=url, presets=presets, expected_selector='.styles_paragraph__wEGPz') as driver:
                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)
