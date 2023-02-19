import json

from chrome_parsing import CopyPageOneFilm, FindFilmsLinks, FindInfoOneFilm
from movies_list import movie_lst


def start(parsing_links_films=False, parsing_films=False, collect_json=True):
    """Проход по основным страницам с фильмами их сохранение и парсинг ссылок на фильмы"""
    f = FindFilmsLinks(pars_mode=parsing_links_films)
    links_films = f.get_films_list()

    """Проход по ссылкам конкретных фильмов и сохранение страниц"""
    pars = CopyPageOneFilm(pars_mode=parsing_films)
    pars.copy_html_films(movie_lst)

    if collect_json:
        """Парсинг страниц каждого фильма"""
        data_json = {}
        for x in range(1, 251):
            try:
                obj_film = FindInfoOneFilm(x)
                obj_film_json = obj_film.get_json_parsing()
                print(obj_film_json)
                data_json[x] = obj_film_json
            except Exception as err:
                print(err)

        with open('movies_info.json', 'w') as file:
            json.dump(data_json, file, ensure_ascii=False)
