from dataclasses import dataclass
from typing import Optional


@dataclass
class MovieFields:
    kp_url: str
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
    synopsys: str
    image: str
    kp_rating: float
    kp_count: int
    imdb_rating: Optional[float]
    imdb_count: Optional[int]


@dataclass
class Movie:
    pk: int
    fields: MovieFields
    model: str = 'movies.movie'


@dataclass
class PersonFields:
    kp_url: str
    rus_name: str
    orig_name: Optional[str]
    birth_date: Optional[str]
    death_date: Optional[str]
    image: Optional[str]
    motherland: Optional[int]


@dataclass
class Person:
    pk: int
    fields: PersonFields
    model: str = 'movies.person'


@dataclass
class GenreFields:
    name: str


@dataclass
class Genre:
    pk: int
    fields: GenreFields
    model: str = 'movies.genre'


@dataclass
class CountryFields:
    name: str


@dataclass
class Country:
    pk: int
    fields: CountryFields
    model: str = 'movies.country'


@dataclass
class MovieStillFields:
    movie: int
    image: str


@dataclass
class MovieStill:
    pk: int
    fields: MovieStillFields
    model: str = 'movies.moviestill'
