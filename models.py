from dataclasses import dataclass
from typing import Optional


@dataclass
class Movie:
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
class Person:
    kp_url: str
    rus_name: str
    orig_name: Optional[str]
    birth_date: Optional[str]
    death_date: Optional[str]
    image: Optional[str]
    motherland: Optional[int]


@dataclass
class Genre:
    name: str


@dataclass
class Country:
    name: str


@dataclass
class MovieStill:
    movie: int
    image: str
