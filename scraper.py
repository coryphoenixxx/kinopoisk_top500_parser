import time
from shutil import rmtree

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from utils.file_manager import fm
from utils.url_manager import urls
from utils.utils import parallel_run


class Scraper:
    def solve_captchas(self):
        file = fm.solved_captchas
        if file.exists():
            data = file.read()
            if len(data) >= config.proc_num and all(data):
                print("Решение капчи не требуется...")
                return

        rmtree(fm.user_data.obj)

        result = parallel_run(
            target=self._solve_capthas_job,
            tasks=[urls.base] * config.proc_num,
            webdriver=True,
            pbar_desc="Решение капчи",
            result_type=list,
        )

        file.write(result)

    def download_movie_list_pages(self):
        file = fm.movies_data
        if not file.exists():
            parallel_run(
                target=self._download_movie_list_pages_job,
                tasks=urls.movie_lists,
                webdriver=True,
                pbar_desc="Скачивание страниц со списками фильмов",
            )
        else:
            print("Скачивание страниц со списками фильмов не требуется...")

    def download_movie_pages(self):
        json_dict = fm.movies_data.read()

        movie_urls_with_pos = [(int(item[0]), item[1]['url']) for item in json_dict.items()]

        parallel_run(
            target=self._download_movie_pages_job,
            tasks=movie_urls_with_pos,
            webdriver=True,
            pbar_desc="Скачивание страниц фильмов",
        )

    @staticmethod
    def _solve_capthas_job(url_q, result, presets, pbar):
        preset = presets.get()
        url = url_q.get()

        while True:
            with WebDriver(preset=preset, js=True, tease_captcha=True) as driver:
                for i in range(10):
                    driver.get(url)
                    if 'showcaptcha' in driver.current_url:
                        break

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
        result.append(True)

    @staticmethod
    def _download_movie_list_pages_job(url_q, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                url = url_q.get()
                number = int(url.split('page=')[-1])

                driver.get(url, expected_selector='.styles_root__ti07r')

                file = fm.movie_list_html(number)
                file.write(driver.page_source)

                pbar.put_nowait(1)

    @staticmethod
    def _download_movie_pages_job(url_q, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                number, url = url_q.get()

                driver.get(url, expected_selector='.styles_paragraph__wEGPz')

                file = fm.movie_html(number)
                file.write(driver.page_source)

                pbar.put_nowait(1)
