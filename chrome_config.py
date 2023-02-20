from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
# options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_experimental_option("excludeSwitches", ["enable-automation"])


class Navigator:
    @staticmethod
    def get_one_movie_path(num: int) -> str:
        """Функция отвечает за выдачу ссылки на один фильм"""
        return f'./pages_movies/movie_{num}.html'

    @staticmethod
    def get_movies_page_path(num: int) -> str:
        """Функция отвечает за нумерацию общих страниц с фильмами"""
        return f'./pages_list_movies/movies_page_{num}.html'
