from parser import Parser
from scraper import Scraper
from utils import timeit


@timeit
def main():
    scraper, parser = Scraper(), Parser()

    scraper.download_movie_list_pages()
    parser.extract_movie_urls()
    scraper.download_movie_pages()


if __name__ == '__main__':
    main()
