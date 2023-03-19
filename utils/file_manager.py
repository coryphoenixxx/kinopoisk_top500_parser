import json
from pathlib import Path
from shutil import rmtree


class StorageUnit:
    """Абстрактный класс элемента файловой системы"""

    def __init__(self, path: str, pdir: str = 'data'):
        self.root_dir = Path(__file__).resolve().parent.parent  # папка проекта
        self.path = self.root_dir / pdir / path  # полный путь до элемента
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def exists(self):
        return self.path.exists()

    def delete(self):
        rmtree(self.path)


class JsonFile(StorageUnit):
    def read(self, model=None):
        """
        :param model: Датакласс модели
        :return: Словарь или датакласс с данными из файла
        """
        with self.path.open(mode='r', encoding='utf-8') as f:
            data = json.load(f)

        if model:
            return [model(**d) for d in data]
        return data

    def write(self, data):
        with self.path.open(mode='w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)

    @property
    def stem(self):
        return self.path.stem


class Dir(StorageUnit):
    def mkdir(self):
        self.path.mkdir(parents=True, exist_ok=True)
        return self.path


class Storage:
    @staticmethod
    def driver_dir(i):
        return Dir(f'drivers/driver_{i}')

    @property
    def chrome_profiles_dir(self):
        return Dir('chrome_profiles')

    @property
    def solved_captchas_json(self):
        return JsonFile('chrome_profiles/solved_captchas.json')

    @staticmethod
    def user_data_dir(i):
        return Dir(f'chrome_profiles/user_data_{i}')

    @property
    def correct_countries_json(self):
        return JsonFile('correct_countries.json', pdir='utils')

    @property
    def movies_data_json(self):
        return JsonFile('movies_data.json')

    @property
    def persons_data_json(self):
        return JsonFile('persons_data.json')

    @property
    def persons_images_dir(self):
        return Dir('media/persons/')

    @property
    def movies_images_dir(self):
        return Dir('media/movies/')

    @staticmethod
    def poster_dir(movie_id):
        return Dir(f'media/movies/{movie_id}/')

    @staticmethod
    def stills_dir(movie_id):
        return Dir(f'media/movies/{movie_id}/stills/')

    @staticmethod
    def photo_dir(person_id):
        return Dir(f'media/persons/{person_id}/')

    @property
    def fixtures_json(self):
        return JsonFile('fixtures.json')


storage = Storage()
