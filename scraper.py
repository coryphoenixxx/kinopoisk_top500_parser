import json

from custom_webriver import WebDriver
from utils import run_in_parallel, get_file


class Scraper:
    def __init__(self):
        self.movie_list_urls = [f"https://www.kinopoisk.ru/lists/movies/top500/?page={i + 1}" for i in range(10)]

    def download_movie_list_pages(self):
        run_in_parallel(
            target=self._download_movie_list_pages_job,
            tasks=self.movie_list_urls,
            webdriver=True,
            pbar_desc="Скачивание страниц со списками фильмов",
        )

    def download_movie_pages(self):
        file = get_file(filepath='data/movie_urls.json')

        with file.open(mode='r', encoding='utf-8') as f:
            json_dict: dict = json.load(f)

        movies_urls = [item.values() for item in json_dict['movies']]

        run_in_parallel(
            target=self._download_movie_pages_job,
            tasks=movies_urls,
            webdriver=True,
            pbar_desc="Скачивание страниц фильмов",
        )

    @staticmethod
    def _download_movie_list_pages_job(urls_queue, presets, pbar):
        while not urls_queue.empty():
            url = urls_queue.get()
            number = url.split('page=')[-1]

            file = get_file(filepath=f'data/pages/movie_lists/page_{number}.html')

            with WebDriver(url=url, presets=presets, expected_selector='.styles_root__ti07r') as driver:
                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)

    @staticmethod
    def _download_movie_pages_job(urls_queue, presets, pbar):
        while not urls_queue.empty():
            number, url = urls_queue.get()

            file = get_file(filepath=f'data/pages/movies/movie_{number}.html')

            with WebDriver(url=url, presets=presets) as driver:
                with file.open(mode='w', encoding='utf-8') as f:
                    f.write(driver.page_source)

                pbar.put_nowait(1)
