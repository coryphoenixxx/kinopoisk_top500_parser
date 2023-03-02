import json
from pathlib import Path

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

        parallel_run(
            target=self._extract_movies_data_job,
            tasks=movies_pages,
            pbar_desc="Извлечение информации о фильме",
        )

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
    def _extract_movies_data_job(files_queue, pbar):
        while not files_queue.empty():
            file = files_queue.get()

            with file.open(mode='r', encoding='utf-8') as f:
                extractor = ProxyExtractor(f)

                print(extractor.movie.rus_title)
                print(extractor.movie.orig_title)
                print(extractor.movie.year)
                print(extractor.movie.countries)
                print(extractor.movie.duration)
                print(extractor.movie.tagline)
                print(extractor.movie.genres)
                print(extractor.movie.directors)
                print(extractor.movie.writers)

            pbar.put_nowait(1)
