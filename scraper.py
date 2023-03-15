from functools import reduce
from operator import itemgetter, add

from config import config
from custom_webriver import WebDriver
from downloader import ImageDownloader
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

        file_m.chrome_profiles_dir.delete()

        result = parallel_run(
            target=self._solve_capthas_process_job,
            tasks=[url_m.base] * config.proc_num,
            result_type=list,
            pbar_params=("Решение капчи", config.proc_num),
        )

        file.write(result)

    @staticmethod
    def _solve_capthas_process_job(urls, result, presets, pbar):
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

    def get_movies_data(self):
        if not file_m.movies_data_json.exists():
            movies_data = parallel_run(
                target=self._get_movies_data_process_job,
                tasks=url_m.movie_lists,
                result_type=dict,
                temp_storage=True,
                pbar_params=("Извлечение информации о фильмах", config.movie_list_num * 50),
            )

            file_m.movies_data_json.write(movies_data)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _get_movies_data_process_job(movie_lists_urls, numbered_movies_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not movie_lists_urls.empty():
                driver.get(movie_lists_urls.get(), expected_selector='.styles_root__ti07r')

                pos_url_tuples = list(MovieListParser(driver.page_source).as_dict().items())

                for t in pos_url_tuples:
                    numbered_movies_urls.put(t)

            while not numbered_movies_urls.empty():
                pos, url = numbered_movies_urls.get()

                driver.get(url, expected_selector='.styles_actors__wn_C4')

                movie_data = MovieParser(driver.page_source).as_dict()

                driver.get(url_m.movie_stills(url), expected_selector='.styles_download__kQ848')

                movie_stills = []
                if 'stills' in driver.current_url:
                    parser = MovieStillsParser(driver.page_source)
                    movie_stills.extend(parser.images_urls)

                if len(movie_stills) < config.still_num:
                    driver.get(url_m.movie_screenshots(url), expected_selector='.styles_download__kQ848')

                    if 'screenshots' in driver.current_url:
                        parser = MovieStillsParser(driver.page_source)
                        screenshots_urls = parser.images_urls[:config.still_num - len(movie_stills)]
                        movie_stills.extend(screenshots_urls)

                movie_data['stills'] = movie_stills
                movie_data['kp_url'] = url

                result[pos] = movie_data
                pbar.put_nowait(1)

    def get_persons_data(self):
        if not file_m.persons_data_json.exists():
            movies_data = file_m.movies_data_json.read()

            persons_urls = set()
            for data in movies_data.values():
                persons_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(data))
                )

            persons_data = parallel_run(
                target=self._get_persons_data_process_job,
                tasks=persons_urls,
                result_type=list,
                pbar_params=("Извлечение информации о персонах...", len(persons_urls)),
            )

            numbered_persons_data = []
            for i, data in enumerate(persons_data, start=1):
                numbered_persons_data.append({'person_id': i} | data)

            file_m.persons_data_json.write(numbered_persons_data)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def _get_persons_data_process_job(persons_urls, result: list, presets, pbar):
        correct_countries = file_m.correct_countries_json.read()

        with WebDriver(preset=presets.get()) as driver:
            while not persons_urls.empty():
                url = persons_urls.get()
                driver.get(url, expected_selector='.styles_primaryName__2Zu1T')

                data = PersonParser(driver.page_source).as_dict()

                c = correct_countries.get(data['motherland'])
                if c:
                    data['motherland'] = c

                result.append({'kp_url': url} | data)
                pbar.put_nowait(1)

    @staticmethod
    def download_images():
        if not file_m.movies_images_dir.exists():
            movies_data = file_m.movies_data_json.read()

            posters_urls = [(movie_id, data['image']) for movie_id, data in movies_data.items()]
            downloader = ImageDownloader(
                numbered_urls=posters_urls,
                download_dir_creator=file_m.poster_dir,
                prefix='poster',
                extension='webp',
                pbar_desc="Скачивание постеров",
            )
            downloader.run()

            stills_urls = []
            for movie_id, data in movies_data.items():
                stills_urls.extend([(movie_id, still_url) for still_url in data['stills']])

            downloader = ImageDownloader(
                numbered_urls=stills_urls,
                download_dir_creator=file_m.stills_dir,
                prefix='still',
                extension='jpg',
                pbar_desc="Скачивание кадров",
                need_number=True,
            )
            downloader.run()
        else:
            print("Скачивание изображений по фильмам не требуется...")

        if not file_m.persons_images_dir.exists():
            persons_data = file_m.persons_data_json.read()

            photos_urls = []
            for data in persons_data:
                photo_url = data.get('image')
                if photo_url:
                    photos_urls.append((data['person_id'], photo_url))

            downloader = ImageDownloader(
                numbered_urls=photos_urls,
                download_dir_creator=file_m.photo_dir,
                prefix='photo',
                extension='webp',
                pbar_desc="Скачивание фотографий персон", )

            downloader.run()
        else:
            print("Скачивание изображений по персонам не требуется...")


scraper = Scraper()
