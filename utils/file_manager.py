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


class JsonFile(StorageUnit):
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
    def solved_captchas_json(self):
        return JsonFile('solved_captchas.json')

    @property
    def chrome_profiles_dir(self):
        return Dir('chrome_profiles')

    @staticmethod
    def user_data_dir(i):
        return Dir(f'chrome_profiles/user_data_{i}')

    @property
    def movies_urls_json(self):
        return JsonFile('movies_urls.json')

    @property
    def movies_data_without_stills_json(self):
        return JsonFile('movies_data_without_stills.json')

    @property
    def full_movies_data_json(self):
        return JsonFile('full_movies_data.json')

    @property
    def persons_data_json(self):
        return JsonFile('persons_data.json')


file_m = FileManager()
