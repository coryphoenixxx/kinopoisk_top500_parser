from dataclasses import asdict
from multiprocessing import Queue, Value
from multiprocessing.managers import ListProxy

from config import config
from image_downloader import ImageDownloader
from models import Person, Movie
from parsers import PersonParser, MovieListParser, MovieParser, MovieStillsParser
from utils.custom_webriver import WebDriver
from utils.file_manager import storage
from utils.utils import parallel_run


class Scraper:
    """Класс скрапинга инфомации по фильмам"""

    @staticmethod
    def _solve_capthas_process_job(kp_urls: Queue, result: ListProxy, presets: Queue, pbar: Queue):
        """
        kp_urls: Очередь со сслыками на kinopoisk
        :param result: Список для фиксирования факта решенной капчи для каждого процесса в файле,
        чтобы при последующих запусках парсера пропускать этот этап
        """

        kp_url = kp_urls.get()

        preset = presets.get()
        for _ in range(3):
            # Провоцирование появление капчи в режиме инкогнито
            with WebDriver(preset=preset, js=False, images=False, incognito=True) as driver:
                while True:
                    driver.get(kp_url)
                    driver.get(config.movie_lists_urls[0])
                    if 'showcaptcha' in driver.current_url:
                        break

            # Решение капчи после перезагрузки вебдрайвера
            with WebDriver(preset=preset, js=True, images=True, captcha_result=True) as driver:
                solved = driver.get(kp_url)
                if solved:
                    break

        pbar.put_nowait(1)
        result.append(True)

    def get_movies_data(self):
        """Получить ссылки на фильмы и распарсить нужную информацию со страниц фильмов"""

        if not storage.movies_data_json.exists():
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

            storage.movies_data_json.write(movies)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _get_movies_urls_process_job(movie_lists_urls: Queue, result: ListProxy, presets: Queue, pbar: Queue):
        """
        :param movie_lists_urls: Очередь со ссылками на страницы-списки
        :param result: Список ссылок на страницы с фильмами
        """

        with WebDriver(preset=presets.get()) as driver:
            while not movie_lists_urls.empty():
                driver.get(movie_lists_urls.get(), expected_selector='.styles_root__ti07r')

                movie_id_url_tuples = MovieListParser(driver.page_source).data.items()

                result.extend(movie_id_url_tuples)
                pbar.put_nowait(1)

    @staticmethod
    def _get_movies_data_process_job(movie_ids_urls: Queue, result: ListProxy, presets: Queue, pbar: Queue):
        """
        :param movie_ids_urls: Очередь с кортежами вида (позиция фильма, ссылка на фильм)
        :param result: Данные по фильмам
        """

        with WebDriver(preset=presets.get()) as driver:
            while not movie_ids_urls.empty():
                movie_id, movie_url = movie_ids_urls.get()

                driver.get(movie_url, expected_selector='.styles_actors__wn_C4')

                movie = MovieParser(driver.page_source).data
                movie.id, movie.kp_url = movie_id, movie_url

                driver.get(movie_url + 'stills/', expected_selector='.styles_download__kQ848')

                # Собрать ссылки на кадры. Если их их меньше, чем указано в STILLS_NUM, то добрать скриншотами
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
        """Получить данные по персонам (актеры, сценаристы, режиссеры), которые указаны на главных страницах фильмов"""

        if not storage.persons_data_json.exists():
            movies = storage.movies_data_json.read(Movie)

            persons_urls = set()
            for movie in movies:
                for role_key in ('actors', 'directors', 'writers'):
                    persons_urls.update(getattr(movie, role_key))

            persons = parallel_run(
                target=self._get_persons_data_process_job,
                tasks=persons_urls,
                counter=True,
                pbar_desc="Извлечение информации о персонах...",
            )

            storage.persons_data_json.write(persons)
        else:
            print("Извлечение информации по персонам не требуется...")

    @staticmethod
    def _get_persons_data_process_job(
            persons_urls: Queue,
            result: ListProxy,
            presets: Queue,
            pbar: Queue,
            counter: Value
    ):
        """
        :param persons_urls: Очередь со ссылками на персоны
        :param result: Список данных о персонах
        :param counter: Счетчик персон (для нумерации)
        """

        correct_countries = storage.correct_countries_json.read()

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
        """Асинхронная закачка постеров, кадров и фотографий персон. Сложить все по папкам в /media"""

        if not storage.movies_images_dir.exists():
            movies = storage.movies_data_json.read(Movie)

            posters_urls = [(movie.id, movie.image) for movie in movies]
            downloader = ImageDownloader(
                numbered_urls=posters_urls,
                download_dir_creator=storage.poster_dir,
                filename='poster',
                extension='webp',
                pbar_desc="Скачивание постеров",
            )
            downloader.run()

            stills_urls = [(movie.id, still_url) for movie in movies for still_url in movie.stills]
            downloader = ImageDownloader(
                numbered_urls=stills_urls,
                download_dir_creator=storage.stills_dir,
                filename='still',
                need_number=True,
                extension='jpg',
                pbar_desc="Скачивание кадров",
            )
            downloader.run()
        else:
            print("Скачивание изображений по фильмам не требуется...")

        if not storage.persons_images_dir.exists():
            persons = storage.persons_data_json.read(Person)

            photos_urls = [(person.id, person.image) for person in persons if person.image]
            downloader = ImageDownloader(
                numbered_urls=photos_urls,
                download_dir_creator=storage.photo_dir,
                filename='photo',
                extension='webp',
                pbar_desc="Скачивание фотографий персон",
            )
            downloader.run()
        else:
            print("Скачивание изображений по персонам не требуется...")


scraper = Scraper()
