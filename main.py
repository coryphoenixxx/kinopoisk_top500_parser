from dotenv import load_dotenv

from parser import parser
from scraper import scraper
from utils.utils import timeit

load_dotenv()


@timeit
def main():
    scraper.download_movie_list_pages()
    parser.extract_movie_urls()
    scraper.download_movie_pages()
    parser.extract_movie_data()
    scraper.collect_movie_still_urls()


if __name__ == '__main__':
    scraper.solve_captchas()
    main()
