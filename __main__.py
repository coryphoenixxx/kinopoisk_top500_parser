from fixtures import FixturesCreator
from scraper import scraper
from utils.file_manager import storage
from utils.utils import timeit, show_countries


@timeit
def scrape():
    scraper.get_movies_data()
    scraper.get_persons_data()
    scraper.download_images()


if __name__ == '__main__':
    scraper.solve_captchas()
    scrape()

    show_countries()
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
            show_countries()

    storage.fixtures_json.write(FixturesCreator().run())
