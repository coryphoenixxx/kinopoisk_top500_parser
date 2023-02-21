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

from chrome_config import options
from utils import Navigator

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



