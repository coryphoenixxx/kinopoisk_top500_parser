class UrlManager:
    def __init__(self):
        self.base = 'https://www.kinopoisk.ru'
        self.movie_lists = [f"{self.base}/lists/movies/top500/?page={i + 1}" for i in range(10)]

    @staticmethod
    def movie_stills(movie_url):
        return movie_url + 'stills/'

    @staticmethod
    def movie_screenshots(movie_url):
        return movie_url + 'screenshots/'

    def person_number_to_url(self, number):
        return self.base + f'/name/{number}/'


url_m = UrlManager()
