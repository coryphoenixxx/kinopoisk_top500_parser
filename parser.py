import json
from pathlib import Path, WindowsPath
from pprint import pprint

from tqdm import tqdm

from extractor import ProxyExtractor
from utils import get_file, parallel_run


class Parser:
    def extract_movie_urls(self):
        pathdir = Path().resolve() / 'data/pages/movie_lists'
        movie_list_pages = sorted(pathdir.iterdir())

        result = self._extract_movie_urls_job(movie_list_pages)

        json_dict = {}
        file = get_file(path='data/movie_urls.json')

        with file.open(mode='w', encoding='utf-8') as f:
            json_dict['movies'] = result
            json.dump(json_dict, f, ensure_ascii=False, sort_keys=True, indent=4)

    def extract_movies_data(self):
        pathdir = Path().resolve() / 'data/pages/movies'
        movies_pages = sorted(pathdir.iterdir())

        result = parallel_run(
            target=self._extract_movies_data_job,
            tasks=movies_pages,
            pbar_desc="Извлечение информации о фильме",
            shared_result=True
        )

        # pprint(result, width=120)

    @staticmethod
    def _extract_movie_urls_job(files):
        result = []
        for file in tqdm(files, desc="Извлечение ссылок на фильмы"):
            with file.open(mode='r', encoding='utf-8') as f:
                positions, urls = ProxyExtractor(f).movie.urls

                for pos, url in zip(positions, urls):
                    result.append({
                        'position': int(pos.text),
                        'url': 'https://www.kinopoisk.ru' + url.get('href')
                    })
        return result

    @staticmethod
    def _extract_movies_data_job(files_queue, result, pbar):
        while not files_queue.empty():
            file = get_file(path='data/movie_urls.json')

            with file.open(mode='r', encoding='utf-8') as f:
                json_dict: dict = json.load(f)

            file: WindowsPath = files_queue.get()

            pos = int(str(file).split('.')[0].split('\\')[-1].split('_')[-1])

            with file.open(mode='r', encoding='utf-8') as f:
                extractor = ProxyExtractor(f)

                d = {
                    'rus_title': extractor.movie.rus_title,
                    'orig_title': extractor.movie.orig_title,
                    'year': extractor.movie.year,
                    'countries': extractor.movie.countries,
                    'duration': extractor.movie.duration,
                    'tagline': extractor.movie.tagline,
                    'genres': extractor.movie.genres,
                    'directors': extractor.movie.directors,
                    'writers': extractor.movie.writers,
                    'description': extractor.movie.description,
                    'actors': extractor.movie.actors,
                    'poster': extractor.movie.poster,
                    'kp_rating': extractor.movie.kp_rating,
                    'kp_count': extractor.movie.kp_count,
                    'imdb_rating': extractor.movie.imdb_rating,
                    'imdb_count': extractor.movie.imdb_count,
                }

                pprint(d)
                print()

                result.append(d)
            # pbar.put_nowait(None)
