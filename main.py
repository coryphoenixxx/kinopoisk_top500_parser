from dotenv import load_dotenv

from parser import Parser
from scraper import Scraper
from utils import timeit

load_dotenv()


@timeit
def main():
    scraper, parser = Scraper(), Parser()

    scraper.solve_captchas()
    scraper.download_movie_list_pages()
    parser.extract_movie_urls()
    scraper.download_movie_pages()


if __name__ == '__main__':
    main()
