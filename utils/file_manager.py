import json
from pathlib import Path


class StorageUnit:
    def __init__(self, path):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.obj = self.root_dir / 'data' / path
        self.obj.parent.mkdir(parents=True, exist_ok=True)

        if '.' not in path:
            self.obj.mkdir(parents=True, exist_ok=True)

    def exists(self):
        return self.obj.exists()


class File(StorageUnit):
    def read(self):
        with self.obj.open(mode='r', encoding='utf-8') as f:
            if self.obj.suffix == '.json':
                data = json.load(f)
            else:
                data = f.read()
        if isinstance(data, dict):
            data = {int(k): v for k, v in sorted(data.items(), key=lambda x: (int(x[0]), x[1]))}
        return data

    def write(self, data):
        with self.obj.open(mode='w', encoding='utf-8') as f:
            if self.obj.suffix == '.json':
                json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)
            else:
                f.write(data)

    @property
    def stem(self):
        return self.obj.stem


class Dir(StorageUnit):
    def iterdir(self):
        return self.obj.iterdir()

    def listdir(self):
        return list(self.iterdir())


class FileManager:
    @property
    def solved_captchas(self):
        return File('solved_captchas.json')

    @property
    def user_data(self):
        return Dir('user_data')

    @staticmethod
    def user_data_i(i):
        return Dir(f'user_data/user_data_{i}')

    @property
    def movie_urls(self):
        return File('movie_urls.json')

    @property
    def movie_data_without_stills(self):
        return File('movie_data_without_stills.json')

    @property
    def full_movie_data(self):
        return File('full_movie_data.json')

    @property
    def person_data(self):
        return File('person_data.json')


fm = FileManager()
