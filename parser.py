import json
from pathlib import Path

from tqdm import tqdm

from extractors import MovieListExtractor, MovieExtractor
from utils import get_file, parallel_run


class Parser:
    def extract_movie_urls(self):
        pathdir = Path().resolve() / 'data/pages/movie_lists'
        movie_list_pages = sorted(pathdir.iterdir())

        result = self._extract_movie_urls_job(movie_list_pages)

        file = get_file(path='data/movies.json')

        with file.open(mode='w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, sort_keys=True, indent=4)

    def extract_movies_data(self):
        pathdir = Path().resolve() / 'data/pages/movies'
        movies_pages = sorted(pathdir.iterdir())

        result = parallel_run(
            target=self._extract_movies_data_job,
            tasks=movies_pages,
            pbar_desc="Извлечение информации о фильмах",
            result_type=dict,
            reduced=True,
        )

        file = get_file(path='data/movies.json')
        with file.open(mode='r', encoding='utf-8') as f:
            json_dict: dict = json.load(f)

        result = {pos: data | json_dict[pos] for pos, data in result.items()}

        with file.open(mode='w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    @staticmethod
    def _extract_movie_urls_job(files):
        result = {}
        for file in tqdm(files, desc="Извлечение ссылок на фильмы"):
            with file.open(mode='r', encoding='utf-8') as f:
                result.update(MovieListExtractor(f).as_dict())
        return result

    @staticmethod
    def _extract_movies_data_job(files_queue, result, pbar):
        while not files_queue.empty():
            file = files_queue.get()

            with file.open(mode='r', encoding='utf-8') as f:
                movie_data = MovieExtractor(f).as_dict()

            result[str(int(file.stem))] = movie_data
            pbar.put_nowait(1)
