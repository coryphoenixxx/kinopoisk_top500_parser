from functools import reduce
from operator import itemgetter, add
from shutil import rmtree

from config import config
from custom_webriver import WebDriver
from downloader import ImageDownloader
from parsers import PersonParser, MovieListParser, MovieParser, MovieStillsParser
from utils.file_manager import file_m, Dir
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
            target=self._solve_capthas_process_job,
            tasks=[url_m.base] * config.proc_num,
            result_type=list,
            pbar_desc="Решение капчи",
        )

        file.write(result)

    @staticmethod
    def _solve_capthas_process_job(urls, result, presets, pbar):
        preset = presets.get()
        url = urls.get()

        while True:
            with WebDriver(preset=preset, js=True, images=True, incognito=True) as driver:
                for _ in range(100):
                    driver.get(url)
                    if 'showcaptcha' in driver.current_url:
                        break

            with WebDriver(preset=preset, js=True, images=True, captcha_result=True) as driver:
                solved = driver.get(url)
                if solved:
                    break

        pbar.put_nowait(1)
        result.append(True)

    def collect_movies_urls(self):
        if not file_m.movies_urls_json.exists():
            result = parallel_run(
                target=self._collect_movies_urls_process_job,
                tasks=url_m.movie_lists,
                result_type=list,
                pbar_desc="Извлечение ссылок на фильмы",
                reduced=True,
            )
            file_m.movies_urls_json.write(result)
        else:
            print("Извлечение ссылок на фильмы не требуется...")

    @staticmethod
    def _collect_movies_urls_process_job(urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not urls.empty():
                driver.get(urls.get(), expected_selector='.styles_root__ti07r')

                position_url_tuples = list(MovieListParser(driver.page_source).as_dict().items())

                result.extend(position_url_tuples)
                pbar.put_nowait(1)

    def get_basic_movies_data(self):
        if not file_m.basic_movies_data_json.exists():
            numbered_movies_urls = file_m.movies_urls_json.read()

            result = parallel_run(
                target=self._get_basic_movies_data_process_job,
                tasks=numbered_movies_urls,
                result_type=dict,
                pbar_desc="Извлечение информации о фильмах",
            )

            file_m.basic_movies_data_json.write(result)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _get_basic_movies_data_process_job(numbered_movies_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not numbered_movies_urls.empty():
                pos, url = numbered_movies_urls.get()
                driver.get(url, expected_selector='.styles_actors__wn_C4')

                data = MovieParser(driver.page_source).as_dict()
                data['kp_url'] = url

                result[pos] = data
                pbar.put_nowait(1)

    def collect_movies_still_urls(self):
        if not file_m.movies_stills_urls_json.exists():
            numbered_movies_urls = file_m.movies_urls_json.read()

            result = parallel_run(
                target=self._collect_movies_stills_urls_process_job,
                tasks=numbered_movies_urls,
                result_type=dict,
                pbar_desc="Извлечение ссылок на кадры",
            )

            file_m.movies_stills_urls_json.write(result)
        else:
            print("Извлечение ссылок на кадры не требуется...")

    @staticmethod
    def _collect_movies_stills_urls_process_job(numbered_movies_urls, result, presets, pbar):
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
            movies_data = file_m.basic_movies_data_json.read()

            persons_urls = set()
            for data in movies_data.values():
                persons_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(data))
                )

            result = parallel_run(
                target=self._get_persons_data_process_job,
                tasks=persons_urls,
                result_type=list,
                pbar_desc="Извлечение информации о персонах...",
            )

            file_m.persons_data_json.write(result)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def _get_persons_data_process_job(persons_urls, result: list, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not persons_urls.empty():
                url = persons_urls.get()
                driver.get(url, expected_selector='.styles_primaryName__2Zu1T')

                data = PersonParser(driver.page_source).as_dict()
                if False in data.values():
                    continue

                result.append({'kp_url': url} | data)
                pbar.put_nowait(1)

    @staticmethod
    def download_images():
        if not Dir('/media').exists():
            downloader = ImageDownloader()
            movies_data = file_m.basic_movies_data_json.read()
            numbered_poster_urls = [(k, v['image']) for k, v in movies_data.items()]
            downloader.run(
                numbered_urls=numbered_poster_urls,
                download_dir_creator=file_m.poster_dir,
                prefix='poster',
                extension='webp',
                pbar_desc="Скачивание постеров",
            )

            persons_data = file_m.persons_data_json.read()
            numbered_photo_urls = [(i, v['image']) for i, v in enumerate(persons_data, start=1)]
            downloader.run(
                numbered_urls=numbered_photo_urls,
                download_dir_creator=file_m.photo_dir,
                prefix='photo',
                extension='webp',
                pbar_desc="Скачивание фотографий персон",
            )

            movies_stills_urls = file_m.movies_stills_urls_json.read()
            numbered_still_urls = []
            for i, still_urls in movies_stills_urls.items():
                for url in still_urls:
                    numbered_still_urls.append((i, url))

            downloader.run(
                numbered_urls=numbered_still_urls,
                download_dir_creator=file_m.stills_dir,
                prefix='still',
                extension='jpg',
                pbar_desc="Скачивание кадров",
                need_number=True,
            )
        else:
            print("Скачивание изображений не требуется... (существует папка media)")


scraper = Scraper()
