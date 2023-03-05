import json
from pathlib import Path


class StorageUnit:
    def __init__(self, path):
        self.root_dir = Path(__file__).resolve().parent.parent
        self.obj = self.root_dir / 'data' / path
        self.obj.parent.mkdir(parents=True, exist_ok=True)

    def exists(self):
        return self.obj.exists()


class File(StorageUnit):
    def read(self):
        with self.obj.open(mode='r', encoding='utf-8') as f:
            if self.obj.suffix == '.json':
                data = json.load(f)
            else:
                data = f.read()
        return data

    def write(self, data):
        with self.obj.open(mode='w', encoding='utf-8') as f:
            if self.obj.suffix == '.json':
                json.dump(data, f, ensure_ascii=False, sort_keys=True, indent=4)
            else:
                f.write(data)


class Dir(StorageUnit):
    def iterdir(self):
        return self.obj.iterdir()


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
    def movies_data(self):
        return File('movies_data.json')

    @staticmethod
    def movie_list_html(number):
        return File(f'pages/movie_lists/{number:02d}.html')

    @property
    def movie_lists_html(self):
        return sorted(Dir('pages/movie_lists').iterdir())

    @staticmethod
    def movie_html(number):
        return File(f'pages/movies/{number:03d}.html')

    @property
    def movies_html(self):
        return sorted(Dir('pages/movies').iterdir())


fm = FileManager()
