from typing import List, Union


class Movie:
    def __init__(self):
        self.rus_name: Union[str, None] = None
        self.orig_name: Union[str, None] = None
        self.poster: Union[str, None] = None
        self.frames: Union[str, List[str], None] = None
        self.actors: Union[str, List[str], None] = None
        self.country: Union[str, List[str], None] = None
        self.genres: Union[str, List[str], None] = None
        self.directors: Union[str, List[str], None] = None
        self.screenwriters: Union[str, List[str], None] = None
        self.year: Union[str, None] = None
        self.time: Union[str, None] = None
        self.short_description: Union[str, None] = None
        self.full_description: Union[str, None] = None
        self.kp_rating: Union[str, None] = None
        self.imdb_rating: Union[str, None] = None
        self.link: Union[str, None] = None
        self.trailer: Union[str, None] = None

    def get_movie_dict(self):
        films_dct = {'rus_name': self.rus_name,
                     'orig_name': self.orig_name,
                     'poster': self.poster,
                     'frames': self.frames,
                     'actors': self.actors,
                     'country': self.country,
                     'genres': self.genres,
                     'directors': self.directors,
                     'screenwriters': self.screenwriters,
                     'year': self.year,
                     'time': self.time,
                     'short_description': self.short_description,
                     'full_description': self.full_description,
                     'kp_rating': self.kp_rating,
                     'link': self.link,
                     'trailer': self.trailer,
                     }
        return films_dct
