import re
import time
from functools import reduce
from operator import itemgetter, add
from shutil import rmtree

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from extractors import PersonExtractor
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
            target=self.__solve_capthas_job,
            tasks=[urls.base] * config.proc_num,
            webdriver=True,
            pbar_desc="Решение капчи",
            result_type=list,
        )

        file.write(result)

    @staticmethod
    def __solve_capthas_job(url_q, result, presets, pbar):
        preset = presets.get()
        url = url_q.get()

        while True:
            with WebDriver(preset=preset, js=True, tease_captcha=True) as driver:
                for _ in range(10):
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

    def download_movie_list_pages(self):
        if len(fm.movie_lists_dir.listdir()) < config.movie_list_num:
            parallel_run(
                target=self.__download_movie_list_pages_job,
                tasks=urls.movie_lists,
                webdriver=True,
                pbar_desc="Скачивание страниц со списками фильмов",
                reduced=True,
            )
        else:
            print("Скачивание страниц со списками фильмов не требуется...")

    @staticmethod
    def __download_movie_list_pages_job(url_q, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                url = url_q.get()
                number = int(url.split('page=')[-1])

                driver.get(url, expected_selector='.styles_root__ti07r')

                file = fm.movie_list_html(number)
                file.write(driver.page_source)

                pbar.put_nowait(1)

    def download_movie_pages(self):
        if len(fm.movies_dir.listdir()) < config.movie_num:
            movies_pos_url = fm.movie_urls.read().items()

            parallel_run(
                target=self.__download_movie_pages_job,
                tasks=movies_pos_url,
                webdriver=True,
                pbar_desc="Скачивание страниц фильмов",
            )
        else:
            print("Скачивание страниц с фильмами не требуется...")

    @staticmethod
    def __download_movie_pages_job(url_q, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                pos, url = url_q.get()

                driver.get(url, expected_selector='.styles_actors__wn_C4')

                file = fm.movie_html(pos)
                file.write(driver.page_source)

                pbar.put_nowait(1)

    def collect_movie_still_urls(self):
        if not fm.full_movie_data.exists():
            movies_pos_url = fm.movie_urls.read().items()

            result = parallel_run(
                target=self.__collect_movie_still_urls_job,
                tasks=movies_pos_url,
                webdriver=True,
                result_type=dict,
                pbar_desc="Извлечение ссылок на кадры",
            )

            data = fm.movie_data_without_stills.read()
            for pos, still_urls in result.items():
                data[pos]['stills'] = still_urls

            fm.full_movie_data.write(data)
        else:
            print("Извлечение ссылок на кадры не требуется...")

    @staticmethod
    def __collect_movie_still_urls_job(url_q, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                pos, url = url_q.get()

                driver.get(urls.movie_stills(url), expected_selector='.styles_download__kQ848')

                still_urls = []
                if 'stills' in driver.current_url:
                    still_elems = driver.find_elements(By.CSS_SELECTOR, '.styles_download__kQ848')[:config.still_num]

                    for elem in still_elems:
                        still_urls.append(elem.get_attribute('href'))

                if len(still_urls) < config.still_num:
                    driver.get(urls.movie_screenshots(url), expected_selector='.styles_download__kQ848')

                    if 'screenshots' in driver.current_url:
                        screenshot_elems = driver.find_elements(
                            By.CSS_SELECTOR, '.styles_download__kQ848'
                        )[:config.still_num - len(still_urls)]

                        for elem in screenshot_elems:
                            still_urls.append(elem.get_attribute('href'))

                result[pos] = still_urls

                pbar.put_nowait(1)

    def person_data_extraction(self):
        if not fm.person_data.exists():
            movie_data = fm.full_movie_data.read()

            person_urls = set()
            for _, data in movie_data.items():
                person_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(data))
                )

            result = parallel_run(
                target=self.__person_data_extraction_job,
                tasks=person_urls,
                webdriver=True,
                result_type=list,
                pbar_desc="Извлечение информации о персонах...",
            )

            sorted_person_data_by_url_number = sorted(
                result,
                key=lambda x: int(re.findall(r'name/(\d+)/', x['url'])[0])
            )

            person_data = {i: data for i, data in enumerate(sorted_person_data_by_url_number, start=1)}
            fm.person_data.write(person_data)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def __person_data_extraction_job(url_q, result: list, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                url = url_q.get()

                driver.get(url, expected_selector='.styles_primaryName__2Zu1T')

                extractor = PersonExtractor(driver.page_source)
                if not extractor.person_data_is_correct():
                    continue

                result.append({'url': url} | extractor.as_dict())

                pbar.put_nowait(1)


scraper = Scraper()
