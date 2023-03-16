from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Movie:
    id: int = None
    kp_url: str = None
    rus_title: str = None
    orig_title: Optional[str] = None
    year: int = None
    tagline: Optional[str] = None
    duration: int = None
    synopsys: str = None
    countries: list = field(default_factory=lambda: [])
    genres: list = field(default_factory=lambda: [])
    directors: list = field(default_factory=lambda: [])
    writers: list = field(default_factory=lambda: [])
    actors: list = field(default_factory=lambda: [])
    image: str = None
    stills: list = field(default_factory=lambda: [])
    kp_rating: float = None
    kp_count: int = None
    imdb_rating: Optional[float] = None
    imdb_count: Optional[int] = None


@dataclass(slots=True)
class Person:
    id: int = None
    kp_url: str = None
    rus_name: str = None
    orig_name: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    image: Optional[str] = None
    motherland: Optional[int] = None
