from bs4 import BeautifulSoup

import json
from utils import timeit, Navigator
from movie_model import Movie
from movies_list import movie_lst


class MovieInfoExtractor:
    """
    Сбор информации со страниц каждого фильма.
    Для сбора информации по фильмам используются уже сохраненные страницы.
    """

    def __init__(self, num_film: int):
        self.film = Movie()
        self.num_film = num_film

    def find_rus_name(self, soup):
        class_ = 'styles_title__65Zwx'
        self.film.rus_name = soup.find(class_=class_).text

    def find_orig_name(self, soup):
        try:
            self.film.orig_name = soup.find(class_='styles_originalTitle__JaNKM').text
        except AttributeError:
            self.film.orig_name = None

    def find_poster(self, soup):
        try:
            self.film.poster = soup.find("img",
                                         class_='film-poster styles_root__24Jga styles_rootInDark__64LVq image styles_root__DZigd').text
        except AttributeError:
            self.film.poster = soup.find("img",
                                         class_='film-poster styles_root__24Jga styles_rootInLight__GwYHH image styles_root__DZigd').text

    def find_actors(self, soup):
        try:
            actors = soup.find_all('a', class_="styles_link__Act80")
            self.film.actors = [actor.text.replace('\n                                ', ' ') for actor in actors][0:5]
        except IndexError:
            self.film.actors = None
            print('ошибка find_actors', self.film.orig_name)

    def find_country(self, soup):
        classes = ('styles_rowLight__P8Y_1 styles_row__da_RK', 'styles_rowDark__ucbcz styles_row__da_RK',)

        for class_ in classes:
            try:
                self.film.country = [c.strip() for c in
                                     soup.find_all(class_=class_)[1].text.replace('Страна', '').strip().split(',')]
            except IndexError:
                continue

    def find_genres(self, soup):
        try:
            self.film.genres = [g.strip() for g in
                                soup.find_all(class_='styles_rowDark__ucbcz styles_row__da_RK')[2].text.replace('Жанр',
                                                                                                                '').replace(
                                    'слова',
                                    '').replace(',', '').strip().split()]
        except IndexError:
            try:
                self.film.genres = soup.find_all(class_='styles_rowLight__P8Y_1 styles_row__da_RK')[2].text.replace(
                    'Жанр',
                    '').replace(
                    'слова',
                    '').replace(',', '').strip().split()
            except IndexError:
                self.film.genres = None
                print('ошибка find_genres', self.film.orig_name)

    def find_directors(self, soup):
        try:
            self.film.directors = [d.strip() for d in
                                   soup.find_all(class_='styles_rowDark__ucbcz styles_row__da_RK')[4].text.replace(
                                       'Режиссер',
                                       '').strip().split(',')]
        except IndexError:
            try:
                self.film.directors = [d.strip() for d in
                                       soup.find_all(class_='styles_rowLight__P8Y_1 styles_row__da_RK')[4].text.replace(
                                           'Режиссер',
                                           '').strip().split(',')]
            except IndexError:
                self.film.directors = None
                print('ошибка find_directors', self.film.orig_name)

    def find_screenwriters(self, soup):
        try:
            self.film.screenwriters = [s.strip() for s in
                                       soup.find_all(class_='styles_rowLight__P8Y_1 styles_row__da_RK')[5].text.replace(
                                           'Сценарий', '').split(',') if s != '"..."']

        except IndexError:
            try:
                self.film.screenwriters = [s.strip() for s in
                                           soup.find_all(class_='styles_rowDark__ucbcz styles_row__da_RK')[5]. \
                                               text.replace('Сценарий', '').split(',') if s != '"..."']
            except IndexError:
                self.film.screenwriters = None
                print('ошибка find_screenwriters', self.film.orig_name)

    def find_year(self, soup):
        try:
            self.film.year = soup.find_all(class_='styles_rowLight__P8Y_1 styles_row__da_RK')[0].text.replace(
                'Год производства', '').strip()
        except IndexError:
            try:
                self.film.year = soup.find_all(class_='styles_rowDark__ucbcz styles_row__da_RK')[0].text.replace(
                    'Год производства', '').strip()
            except IndexError:
                print(f'ошибка find_year', self.film.orig_name)

    def find_time(self, soup):
        try:
            self.film.time = soup.find_all(class_='styles_rowLight__P8Y_1 styles_row__da_RK')[-1].text.replace('Время',
                                                                                                               '').strip()[
                             :8]
        except IndexError:

            self.film.time = soup.find_all(class_='styles_rowDark__ucbcz styles_row__da_RK')[
                                 -1].text.replace('Время', '').strip()[:8]

    def find_short_description(self, soup):
        try:
            self.film.short_description = soup.find('p', class_='styles_root__aZJRN').text.replace(
                '\n                           ', ' ').replace(' ', ' ')
        except AttributeError:
            self.film.short_description = None

    def find_full_description(self, soup):
        self.film.full_description = soup.find(class_='styles_paragraph__wEGPz').text.replace(
            '\n                          ', ' ').replace(' ', ' ')

    def find_kp_rating(self, soup):
        self.film.kp_rating = soup.find(class_='styles_ratingKpTop__84afd').text

    def find_trailer(self, soup):
        self.film.trailer = soup.find('a', class_='styles_title__vd96O').text

    def parsing_movie_page(self):
        """Сбор информации со страниц"""
        with open(Navigator.get_one_movie_path(self.num_film), 'r', encoding='utf-8') as file:
            src = file.read()

        soup = BeautifulSoup(src, "lxml")

        self.find_rus_name(soup)
        self.find_orig_name(soup)
        self.find_poster(soup)
        self.find_actors(soup)
        self.find_country(soup)
        self.find_genres(soup)
        self.find_directors(soup)
        self.find_screenwriters(soup)
        self.find_year(soup)
        self.find_time(soup)
        self.find_short_description(soup)
        self.find_full_description(soup)
        self.find_kp_rating(soup)

    def get_json_parsing(self) -> Movie:
        self.parsing_movie_page()
        res: Movie = self.film.get_movie_dict()
        return res


@timeit
def collect_json():
    data_json = {}
    for x in range(1, 251):
        try:  # TODO: избавиться от try .. except
            obj_film = MovieInfoExtractor(x)
            obj_film_json = obj_film.get_json_parsing()
            data_json[x] = obj_film_json
        except Exception as err:
            print(x, err)

    import pprint
    pprint.pprint(data_json)

    with open('movies_info.json', 'w', encoding="utf-8") as file:
        json.dump(data_json, file, ensure_ascii=False)
