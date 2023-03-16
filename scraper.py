from dataclasses import asdict
from functools import reduce
from operator import itemgetter, add

from config import config
from custom_webriver import WebDriver
from downloader import ImageDownloader
from models import Person, Movie
from parsers import PersonParser, MovieListParser, MovieParser, MovieStillsParser
from utils.file_manager import file_m
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
            tasks=[config.base_url] * config.proc_num,
            pbar_desc="Решение капчи",
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
            movie_ids_urls = parallel_run(
                target=self._get_movies_urls_process_job,
                tasks=config.movie_lists_urls,
                pbar_desc="Извлечение ссылок на фильмы",
            )

            movies = parallel_run(
                target=self._get_movies_data_process_job,
                tasks=movie_ids_urls,
                pbar_desc="Извлечение информации о фильмах",
            )

            file_m.movies_data_json.write(movies)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _get_movies_urls_process_job(movie_lists_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not movie_lists_urls.empty():
                driver.get(movie_lists_urls.get(), expected_selector='.styles_root__ti07r')

                movie_id_url_tuples = MovieListParser(driver.page_source).data.items()

                result.extend(movie_id_url_tuples)
                pbar.put_nowait(1)

    @staticmethod
    def _get_movies_data_process_job(movie_ids_urls, result, presets, pbar):
        with WebDriver(preset=presets.get()) as driver:
            while not movie_ids_urls.empty():
                movie_id, movie_url = movie_ids_urls.get()

                driver.get(movie_url, expected_selector='.styles_actors__wn_C4')

                movie = MovieParser(driver.page_source).data
                movie.id, movie.kp_url = movie_id, movie_url

                driver.get(movie_url + 'stills/', expected_selector='.styles_download__kQ848')

                if 'stills' in driver.current_url:
                    parser = MovieStillsParser(driver.page_source)
                    movie.stills.extend(parser.images_urls)

                if len(movie.stills) < config.still_num:
                    driver.get(movie_url + 'screenshots/', expected_selector='.styles_download__kQ848')

                    if 'screenshots' in driver.current_url:
                        parser = MovieStillsParser(driver.page_source)
                        screenshots_urls = parser.images_urls[:config.still_num - len(movie.stills)]
                        movie.stills.extend(screenshots_urls)

                result.append(asdict(movie))
                pbar.put_nowait(1)

    def get_persons_data(self):
        if not file_m.persons_data_json.exists():
            movies = file_m.movies_data_json.read()

            persons_urls = set()
            for movie in movies:
                persons_urls.update(
                    reduce(add, itemgetter('actors', 'directors', 'writers')(movie))
                )

            persons = parallel_run(
                target=self._get_persons_data_process_job,
                tasks=persons_urls,
                counter=True,
                pbar_desc="Извлечение информации о персонах...",
            )

            file_m.persons_data_json.write(persons)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def _get_persons_data_process_job(persons_urls, result, counter, presets, pbar):
        correct_countries = file_m.correct_countries_json.read()

        with WebDriver(preset=presets.get()) as driver:
            while not persons_urls.empty():
                url = persons_urls.get()
                driver.get(url, expected_selector='.styles_primaryName__2Zu1T')

                person = PersonParser(driver.page_source).data

                counter.value += 1
                person.id = counter.value
                person.kp_url = url

                person.motherland = correct_countries.get(person.motherland) or person.motherland

                result.append(asdict(person))
                pbar.put_nowait(1)

    @staticmethod
    def download_images():
        if not file_m.movies_images_dir.exists():
            movies = file_m.movies_data_json.read(Movie)

            posters_urls = [(movie.id, movie.image) for movie in movies]
            downloader = ImageDownloader(
                numbered_urls=posters_urls,
                download_dir_creator=file_m.poster_dir,
                filename='poster',
                extension='webp',
                pbar_desc="Скачивание постеров",
            )
            downloader.run()

            stills_urls = [(movie.id, still_url) for movie in movies for still_url in movie.stills]
            downloader = ImageDownloader(
                numbered_urls=stills_urls,
                download_dir_creator=file_m.stills_dir,
                filename='still',
                need_number=True,
                extension='jpg',
                pbar_desc="Скачивание кадров",
            )
            downloader.run()
        else:
            print("Скачивание изображений по фильмам не требуется...")

        if not file_m.persons_images_dir.exists():
            persons = file_m.persons_data_json.read(Person)

            photos_urls = [(person.id, person.image) for person in persons if person.image]
            downloader = ImageDownloader(
                numbered_urls=photos_urls,
                download_dir_creator=file_m.photo_dir,
                filename='photo',
                extension='webp',
                pbar_desc="Скачивание фотографий персон",
            )
            downloader.run()
        else:
            print("Скачивание изображений по персонам не требуется...")


scraper = Scraper()
