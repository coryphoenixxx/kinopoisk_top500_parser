from dotenv import load_dotenv

from scraper import scraper
from utils.utils import timeit

load_dotenv()


@timeit
def main():
    scraper.movie_urls_positions_extraction()
    scraper.movie_data_extraction()
    scraper.collect_movie_still_urls()
    scraper.person_data_extraction()


if __name__ == '__main__':
    scraper.solve_captchas()
    main()
