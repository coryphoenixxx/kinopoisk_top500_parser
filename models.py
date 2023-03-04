from dataclasses import dataclass
from typing import Optional


@dataclass
class MovieFields:
    url: str
    rus_title: str
    orig_title: Optional[str]
    year: int
    tagline: Optional[str]
    duration: int
    countries: list[int]
    genres: list[int]
    directors: list[int]
    writers: list[int]
    actors: list[int]
    description: str
    poster: str
    kp_rating: float
    kp_count: int
    imdb_rating: float
    imdb_count: int
    price: float = 0.0


@dataclass
class Movie:
    pk: int
    fields: MovieFields
    model: str = 'movies.movie'
