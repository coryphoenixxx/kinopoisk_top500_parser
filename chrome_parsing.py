import time
from typing import List
from bs4 import BeautifulSoup
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver

from movies_list import movie_lst
from chrome_config import options, Navigator
from class_films import Film

"""
Параметр parse_mode в классах FindFilmsLinks и CopyPageOneFilm отвечает за инициализацию WebDriver.
Если HTML страницы уже сохранены, parse_mode устанавливается False.
Сохраненные ссылки уже имеются в модуле movies_list.py, поэтому можно использовать только класс CopyPageOneFilm
"""


class WebDriverMixin:
    """Инициализация WebDriver"""
    service = None
    driver = None

    def __init__(self, pars_mode: bool):
        if pars_mode:
            self.service = Service(executable_path=ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=self.service, options=options)
            self.driver.set_window_size(1920, 1080)


class FindFilmsLinks(WebDriverMixin):
    """Поиск ссылок на фильмы на общих страницах сайта"""

    def __init__(self, pars_mode: bool):
        if pars_mode:
            self.pars_mode = True
            super().__init__(pars_mode=pars_mode)
        else:
            self.pars_mode = False
        self.url = 'https://www.kinopoisk.ru/lists/movies/top250/?page='
        self.pages = 5
        self.films_links = []

    def sending_request_page(self, url, source_page: int, driver: WebDriver) -> None:
        """Отправка запроса на указанный url"""
        url_page = url + f'{source_page}'
        driver.get(url=url_page)
        time.sleep(10)

    def copy_html_films(self, pages) -> None:
        """Проход по страницам"""

        for page in range(1, pages + 1):
            self.sending_request_page(self.url, page, self.driver)

            for _ in range(10):
                body = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

            with open(Navigator.get_movies_page_path(page), "w", encoding="utf-8") as file:
                file.write(self.driver.page_source)

    def find_links_in_html(self) -> None:
        """Поиск ссылок в сохраненном HTML"""
        for nums_page in range(1, self.pages + 1):
            with open(Navigator.get_movies_page_path(nums_page), 'r', encoding='utf-8') as file:
                src = file.read()
                soup = BeautifulSoup(src, "lxml")

                link_films_in_html = soup.find_all('a', class_="styles_poster__gJgwz styles_root__wgbNq")
                for link in link_films_in_html:
                    full_link = 'https://www.kinopoisk.ru' + link.get('href')
                    self.films_links.append(full_link.rstrip('/'))

    def get_films_list(self) -> List[str]:
        """Выдача списка ссылок на конкретные фильмы"""
        if not self.pars_mode:
            self.find_links_in_html()
        else:
            self.copy_html_films(5)
            self.find_links_in_html()
        return self.films_links


class CopyPageOneFilm(WebDriverMixin):
    """Копирование страниц каждого фильма"""

    def __init__(self, pars_mode: bool):
        if pars_mode:
            super().__init__(pars_mode)

    def send_request(self, film_link: str):
        """Отправка запроса"""
        self.driver.get(url=film_link)
        time.sleep(10)

    def copy_html_films(self, films_links: List[str]) -> None:
        """Проход по страницам конкретных фильмов"""

        num_film = 0
        for film_link in films_links:
            num_film += 1

            self.send_request(film_link=film_link)

            if num_film == 1:
                time.sleep(15)

            for _ in range(2):
                body = WebDriverWait(self.driver, 2).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(1)

            with open(Navigator.get_one_movie_path(num_film), "w", encoding="utf-8") as file:
                file.write(self.driver.page_source)


class FindInfoOneFilm:
    """
    Сбор информации со страниц каждого фильма.
    Для сбора информации по фильмам используются уже сохраненные страницы.
    """

    def __init__(self, num_film: int):
        self.film = Film()
        self.num_film = num_film

    def find_rus_name(self, soup):
        class_ = 'styles_title__65Zwx'
        self.film.rus_name = soup.find(class_=class_).text

        # try:
        #     self.film.rus_name = soup.find(
        #         class_='styles_title__65Zwx styles_root__l9kHe styles_root__5sqsd styles_rootInDark__SZlor').text
        # except AttributeError:
        #     self.film.rus_name = soup.find(
        #         class_='styles_title__65Zwx styles_root__l9kHe styles_root__5sqsd styles_rootInLight__juoEZ').text

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

    def find_link(self):
        self.film.link = movie_lst[self.num_film - 1]

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
        self.find_link()

    def get_json_parsing(self) -> Film:
        self.parsing_movie_page()
        res: Film = self.film.get_movie_dict()
        return res
