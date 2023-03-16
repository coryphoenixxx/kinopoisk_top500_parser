from fixtures import FixturesCreator
from scraper import scraper
from utils.file_manager import file_m
from utils.utils import timeit, show_persons_countries


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
        "______________________________________________________________\n"
        "Ручное исправление некорректных данных по странам у персон... \n"
        "(файл data/persons_data.json)"
    )
    while True:
        user_input = input("Ввод команды 'continue' — создать фикстуры, 'show' — показать страны снова:\n")
        if user_input == 'continue':
            break
        elif user_input == 'show':
            show_persons_countries()

    file_m.fixtures_json.write(FixturesCreator().run())
