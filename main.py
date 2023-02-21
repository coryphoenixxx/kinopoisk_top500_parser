from chrome_parsing import CopyPageOneFilm, FindFilmsLinks
from movies_list import movie_lst
from movie_info_extractor import collect_json


def start(parsing_links_films=True, parsing_films=True):
    """Проход по основным страницам с фильмами их сохранение и парсинг ссылок на фильмы"""
    f = FindFilmsLinks(pars_mode=parsing_links_films)
    links_films = f.get_films_list()

    """Проход по ссылкам конкретных фильмов и сохранение страниц"""
    pars = CopyPageOneFilm(pars_mode=parsing_films)
    pars.copy_html_films(movie_lst)


if __name__ == '__main__':
    collect_json()
