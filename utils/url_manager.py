class UrlManager:
    def __init__(self):
        self.base = 'https://www.kinopoisk.ru'
        self.movie_lists = [f"{self.base}/lists/movies/top500/?page={i + 1}" for i in range(10)]


urls = UrlManager()
