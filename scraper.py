import json
import time
from pathlib import Path

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from utils import parallel_run, get_file


class Scraper:
    def __init__(self):
        self.base_url = 'https://www.kinopoisk.ru'

    def solve_captchas(self):
        user_datas_dir = Path().resolve() / 'user_datas'
        profiles_not_exists = [
            not (user_data_dir / 'Default').exists()
            for user_data_dir in user_datas_dir.iterdir()
        ]

        if all(profiles_not_exists):
            parallel_run(
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

            parallel_run(
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

        movies_urls = [item.values() for item in json_dict['movies']]

        parallel_run(
            target=self._download_movie_pages_job,
            tasks=movies_urls,
            webdriver=True,
            pbar_desc="Скачивание страниц фильмов",
        )

    @staticmethod
    def _solve_capthas_job(urls, presets, pbar):
        preset = presets.get()
        url = urls.get()

        while True:
            with WebDriver(preset=preset, js=True) as driver:
                driver.get(url)

                if 'showcaptcha' not in driver.current_url:
                    continue

                try:
                    driver.find_element(By.CSS_SELECTOR, ".CheckboxCaptcha-Button").click()
                except NoSuchElementException:
                    pass  # TODO:

                while 'showcaptcha' in driver.current_url:
                    time.sleep(0.5)

                pbar.put_nowait(1)
                break

    @staticmethod
    def _download_movie_list_pages_job(urls, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not urls.empty():
                url = urls.get()
                driver.get(url, expected_selector='.styles_root__ti07r')

                number = int(url.split('page=')[-1])
                file = get_file(path=f'data/pages/movie_lists/page_{number:02d}.html')

                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)

    @staticmethod
    def _download_movie_pages_job(urls, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not urls.empty():
                number, url = urls.get()

                driver.get(url, expected_selector='.styles_paragraph__wEGPz')

                file = get_file(path=f'data/pages/movies/movie_{number:03d}.html')
                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)
