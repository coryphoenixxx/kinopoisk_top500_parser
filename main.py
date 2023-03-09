from dotenv import load_dotenv

from scraper import scraper
from utils.utils import timeit

load_dotenv()


@timeit
def main():
    scraper.get_movie_urls()
    scraper.get_movies_data_without_stills()
    scraper.get_movies_stills()
    scraper.get_persons_data()


if __name__ == '__main__':
    scraper.solve_captchas()
    main()
