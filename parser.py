import json
from pathlib import Path

from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import get_file


class Parser:
    def extract_movie_urls(self):
        pathdir = Path().resolve() / 'data/pages/movie_lists'
        movies_list_pages = sorted(pathdir.iterdir())

        result = self._extract_movie_urls_job(movies_list_pages)

        json_dict = {}
        file = get_file(filepath='data/movie_urls.json')

        with file.open(mode='w', encoding='utf-8') as f:
            json_dict['movies'] = result
            json.dump(json_dict, f, ensure_ascii=False, sort_keys=True, indent=4)

    @staticmethod
    def _extract_movie_urls_job(files):
        result = []
        for file in tqdm(files, desc="Извлечение ссылок на фильмы"):
            with file.open(mode='r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, "lxml")

                positions = soup.select(selector='.styles_root__ti07r .styles_position__TDe4E')
                urls = soup.select(selector='.styles_root__ti07r .base-movie-main-info_link__YwtP1')

                for pos, url in zip(positions, urls):
                    result.append({
                        'position': int(pos.text),
                        'url': 'https://www.kinopoisk.ru/' + url.get('href')
                    })

        return result
