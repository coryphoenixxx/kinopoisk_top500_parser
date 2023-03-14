from dotenv import load_dotenv

from scraper import scraper
from utils.utils import timeit, show_persons_countries

load_dotenv()


@timeit
def scrape():
    scraper.get_movies_data()
    scraper.get_persons_data()
    scraper.download_images()


if __name__ == '__main__':
    scraper.solve_captchas()
    scrape()

    show_persons_countries()
    print(
        "Ручное исправление некорректных данных по странам у персон... \n"
        "(файл: data/persons_data.json)"
    )
    while True:
        user_input = input("Ввод команды 'exit' — выход, 'show' — показать снова:")
        if user_input == 'exit':
            break
        elif user_input == 'show':
            show_persons_countries()
