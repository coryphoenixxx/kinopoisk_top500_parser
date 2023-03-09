from functools import reduce
from operator import itemgetter, add
from shutil import rmtree

from config import config
from custom_webriver import WebDriver
from parsers import PersonParser, MovieListParser, MovieParser, MovieStillsParser
from utils.file_manager import file_m
from utils.url_manager import url_m
from utils.utils import parallel_run


class Scraper:
    def solve_captchas(self):
        file = file_m.solved_captchas_json
        if file.exists():
            data = file.read()
            if len(data) >= config.proc_num and all(data):
                print("Решение капчи не требуется...")
                return

        rmtree(file_m.chrome_profiles_dir.obj)

        result = parallel_run(
            target=self._solve_capthas_job,
            tasks=[url_m.base] * config.proc_num,
            result_type=list,
            pbar_desc="Решение капчи",
        )

        file.write(result)

    @staticmethod
    def _solve_capthas_job(urls, result, presets, pbar):
        preset = presets.get()
        url = urls.get()

        while True:
            with WebDriver(preset=preset, js=True, images=True, incognito=True) as driver:
                for _ in range(10):
                    driver.get(url)
                    if 'showcaptcha' in driver.current_url:
                        break

            with WebDriver(preset=preset, js=True, images=True, captcha_result=True) as driver:
                solved = driver.get(url)
                if solved:
                    break

        pbar.put_nowait(1)
        result.append(True)

    def get_movie_urls(self):
        if not file_m.movies_urls_json.exists():
            result = parallel_run(
                target=self._get_movies_urls_job,
                tasks=url_m.movie_lists,
                result_type=dict,
                pbar_desc="Извлечение ссылок на фильмы",
                reduced=True,
            )
            file_m.movies_urls_json.write(result)
        else:
            print("Извлечение ссылок на фильмы не требуется...")

    @staticmethod
    def _get_movies_urls_job(urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not urls.empty():
                driver.get(urls.get(), expected_selector='.styles_root__ti07r')

                result.update(MovieListParser(driver.page_source).as_dict())
                pbar.put_nowait(1)

    def get_movies_data_without_stills(self):
        if not file_m.movies_data_without_stills_json.exists():
            numbered_movie_urls = file_m.movies_urls_json.read().items()

            result = parallel_run(
                target=self._get_movies_data_without_stills_job,
                tasks=numbered_movie_urls,
                result_type=dict,
                pbar_desc="Извлечение информации о фильмах",
            )

            data = file_m.movies_urls_json.read()
            for pos, url in data.items():
                result[pos]['url'] = url

            file_m.movies_data_without_stills_json.write(result)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _get_movies_data_without_stills_job(numbered_movies_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not numbered_movies_urls.empty():
                pos, url = numbered_movies_urls.get()
                driver.get(url, expected_selector='.styles_actors__wn_C4')

                result[pos] = MovieParser(driver.page_source).as_dict()
                pbar.put_nowait(1)

    def get_movies_stills(self):
        if not file_m.full_movies_data_json.exists():
            numbered_movies_urls = file_m.movies_urls_json.read().items()

            result = parallel_run(
                target=self._get_movies_stills_job,
                tasks=numbered_movies_urls,
                result_type=dict,
                pbar_desc="Извлечение ссылок на кадры",
            )

            data = file_m.movies_data_without_stills_json.read()
            for pos, stills_urls in result.items():
                data[pos]['stills'] = stills_urls

            file_m.full_movies_data_json.write(data)
        else:
            print("Извлечение ссылок на кадры не требуется...")

    @staticmethod
    def _get_movies_stills_job(numbered_movies_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not numbered_movies_urls.empty():
                pos, url = numbered_movies_urls.get()

                driver.get(url_m.movie_stills(url), expected_selector='.styles_download__kQ848')

                total_images_urls = []
                if 'stills' in driver.current_url:
                    parser = MovieStillsParser(driver.page_source)
                    total_images_urls.extend(parser.images_urls)

                if len(total_images_urls) < config.still_num:
                    driver.get(url_m.movie_screenshots(url), expected_selector='.styles_download__kQ848')

                    if 'screenshots' in driver.current_url:
                        parser = MovieStillsParser(driver.page_source)
                        screenshots_urls = parser.images_urls[:config.still_num - len(total_images_urls)]
                        total_images_urls.extend(screenshots_urls)

                result[pos] = total_images_urls
                pbar.put_nowait(1)

    def get_persons_data(self):
        if not file_m.persons_data_json.exists():
            movie_data = file_m.full_movies_data_json.read()

            persons_urls = set()
            for data in movie_data.values():
                persons_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(data))
                )

            result = parallel_run(
                target=self._get_persons_data_job,
                tasks=persons_urls,
                result_type=list,
                pbar_desc="Извлечение информации о персонах...",
            )

            file_m.persons_data_json.write(result)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def _get_persons_data_job(urls, result: list, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not urls.empty():
                url = urls.get()
                driver.get(url, expected_selector='.styles_primaryName__2Zu1T')

                data = PersonParser(driver.page_source).as_dict()
                if False in data.values():
                    continue

                result.append({'url': url} | data)
                pbar.put_nowait(1)


scraper = Scraper()
