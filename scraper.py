import re
import time
from functools import reduce
from operator import itemgetter, add
from shutil import rmtree

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from config import config
from custom_webriver import WebDriver
from extractors import PersonExtractor, MovieListExtractor, MovieExtractor, MovieStillsExtractor
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
            result_type=list,
            pbar_desc="Решение капчи",
        )

        file.write(result)

    @staticmethod
    def _solve_capthas_job(url_q, result, presets, pbar):
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

    def movie_urls_positions_extraction(self):
        if not fm.movie_urls.exists():
            result = parallel_run(
                target=self._movie_urls_positions_extraction_job,
                tasks=urls.movie_lists,
                result_type=dict,
                pbar_desc="Извлечение ссылок на фильмы",
                reduced=True,
            )
            fm.movie_urls.write(result)
        else:
            print("Извлечение ссылок на фильмы не требуется...")

    @staticmethod
    def _movie_urls_positions_extraction_job(url_q, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not url_q.empty():
                driver.get(url_q.get(), expected_selector='.styles_root__ti07r')
                result.update(MovieListExtractor(driver.page_source).as_dict())
                pbar.put_nowait(1)

    def movie_data_extraction(self):
        if not fm.movie_data_without_stills.exists():
            movies_pos_url = fm.movie_urls.read().items()

            result = parallel_run(
                target=self._movie_data_extraction_job,
                tasks=movies_pos_url,
                result_type=dict,
                pbar_desc="Извлечение информации о фильмах",
            )

            data = fm.movie_urls.read()
            for pos, url in data.items():
                result[pos]['url'] = url

            fm.movie_data_without_stills.write(result)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _movie_data_extraction_job(pos_url_q, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not pos_url_q.empty():
                pos, url = pos_url_q.get()
                driver.get(url, expected_selector='.styles_actors__wn_C4')
                result[pos] = MovieExtractor(driver.page_source).as_dict()
                pbar.put_nowait(1)

    def collect_movie_still_urls(self):
        if not fm.full_movie_data.exists():
            movies_pos_url = fm.movie_urls.read().items()

            result = parallel_run(
                target=self._collect_movie_still_urls_job,
                tasks=movies_pos_url,
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
    def _collect_movie_still_urls_job(pos_url_q, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not pos_url_q.empty():
                pos, url = pos_url_q.get()

                driver.get(urls.movie_stills(url), expected_selector='.styles_download__kQ848')

                still_urls = []
                if 'stills' in driver.current_url:
                    extractor = MovieStillsExtractor(driver.page_source)
                    still_urls.extend(extractor.get_still_urls())

                if len(still_urls) < config.still_num:
                    driver.get(urls.movie_screenshots(url), expected_selector='.styles_download__kQ848')

                    if 'screenshots' in driver.current_url:
                        extractor = MovieStillsExtractor(driver.page_source)
                        still_urls.extend(extractor.get_screenshot_urls(still_urls))

                result[pos] = still_urls
                pbar.put_nowait(1)

    def person_data_extraction(self):
        if not fm.person_data.exists():
            movie_data = fm.full_movie_data.read()

            person_urls = set()
            for data in movie_data.values():
                person_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(data))
                )

            result = parallel_run(
                target=self._person_data_extraction_job,
                tasks=person_urls,
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
    def _person_data_extraction_job(url_q, result: list, presets, pbar):
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
