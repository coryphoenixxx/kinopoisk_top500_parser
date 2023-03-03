from dotenv import load_dotenv

from parser import Parser
from scraper import Scraper
from utils import timeit

load_dotenv()
scraper, parser = Scraper(), Parser()


@timeit
def main():
    # scraper.solve_captchas()
    scraper.download_movie_list_pages()
    parser.extract_movie_urls()
    scraper.download_movie_pages()
    parser.extract_movies_data()


if __name__ == '__main__':
    main()
