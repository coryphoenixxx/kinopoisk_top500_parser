import json

from chrome_parsing import CopyPageOneFilm, FindFilmsLinks, FindInfoOneFilm
from movies_list import movie_lst

from utils import timeit


def start(parsing_links_films=True, parsing_films=True):
    """Проход по основным страницам с фильмами их сохранение и парсинг ссылок на фильмы"""
    f = FindFilmsLinks(pars_mode=parsing_links_films)
    links_films = f.get_films_list()

    """Проход по ссылкам конкретных фильмов и сохранение страниц"""
    pars = CopyPageOneFilm(pars_mode=parsing_films)
    pars.copy_html_films(movie_lst)


@timeit
def collect_json():
    data_json = {}
    for x in range(1, 251):
        try:  # TODO: избавиться от try .. except
            obj_film = FindInfoOneFilm(x)
            obj_film_json = obj_film.get_json_parsing()
            data_json[x] = obj_film_json
        except Exception as err:
            print(x, err)

    import pprint
    pprint.pprint(data_json)

    with open('movies_info.json', 'w', encoding="utf-8") as file:
        json.dump(data_json, file, ensure_ascii=False)


if __name__ == '__main__':
    start()
