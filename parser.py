from tqdm import tqdm

from extractors import MovieListExtractor, MovieExtractor
from utils.file_manager import fm
from utils.utils import parallel_run


class Parser:
    def extract_movie_urls(self):
        if not fm.movie_urls.exists():
            result = self._extract_movie_urls_job(fm.movie_list_htmls)
            fm.movie_urls.write(result)
        else:
            print("Извлечение ссылок на фильмы не требуется...")

    def extract_movie_data(self):
        if not fm.movie_data_without_stills.exists():
            result = parallel_run(
                target=self._extract_movie_data_job,
                tasks=fm.movie_htmls,
                pbar_desc="Извлечение информации о фильмах",
                result_type=dict,
                reduced=True,
            )

            data = fm.movie_urls.read()
            for pos, url in data.items():
                result[pos]['url'] = url

            fm.movie_data_without_stills.write(result)
        else:
            print("Извлечение информации о фильмах не требуется...")

    @staticmethod
    def _extract_movie_urls_job(files):
        result = {}
        for file in tqdm(files, desc="Извлечение ссылок на фильмы"):
            result.update(MovieListExtractor(file.read()).as_dict())
        return result

    @staticmethod
    def _extract_movie_data_job(file_q, result, pbar):
        while not file_q.empty():
            file = file_q.get()

            movie_data = MovieExtractor(file.read()).as_dict()

            result[int(file.stem)] = movie_data

            pbar.put_nowait(1)


parser = Parser()
