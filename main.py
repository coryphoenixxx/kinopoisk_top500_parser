from dotenv import load_dotenv

from scraper import scraper
from utils.utils import timeit, show_persons_countries

load_dotenv()


@timeit
def scrape():
    scraper.collect_movies_urls()
    scraper.get_basic_movies_data()
    scraper.collect_movies_still_urls()
    scraper.get_persons_data()
    scraper.download_images()


@timeit
def normalize():
    ...


if __name__ == '__main__':
    scraper.solve_captchas()
    scrape()

    show_persons_countries()
    print(
        "Ручное исправление кривых стран у персон... \n"
        "(файл: data/persons_data.json)\n"
        "'exit' — выход, 'show' — показать снова:"
    )
    while True:
        user_input = input()
        if user_input == 'exit':
            break
        elif user_input == 'show':
            show_persons_countries()

    normalize()
