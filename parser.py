from tqdm import tqdm

from extractors import MovieListExtractor, MovieExtractor
from utils.file_manager import fm
from utils.utils import parallel_run


class Parser:
    def extract_movie_urls(self):
        result = self._extract_movie_urls_job(fm.movie_lists_html)
        fm.movies_data.write(result)

    def extract_movies_data(self):
        result = parallel_run(
            target=self._extract_movies_data_job,
            tasks=fm.movies_html,
            pbar_desc="Извлечение информации о фильмах",
            result_type=dict,
            reduced=True,
        )

        json_dict = fm.movies_data.read()
        result = {pos: data | json_dict[pos] for pos, data in result.items()}
        fm.movies_data.write(result)

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
