from collections import defaultdict
from dataclasses import dataclass, asdict, field
from itertools import count

from models import Movie, Person
from utils.file_manager import file_m


@dataclass
class MovieFixture:
    pk: int
    fields: field(default_factory=lambda: {})
    model: str = 'movies.movie'


@dataclass
class PersonFixture:
    pk: int
    fields: field(default_factory=lambda: {})
    model: str = 'movies.person'


@dataclass
class GenreFixture:
    pk: int
    fields: field(default_factory=lambda: {})
    model: str = 'movies.genre'


@dataclass
class CountryFixture:
    pk: int
    fields: field(default_factory=lambda: {})
    model: str = 'movies.country'


@dataclass
class MovieStillFixture:
    pk: int
    fields: field(default_factory=lambda: {})
    model: str = 'movies.moviestill'


class FixturesCollector:
    def __init__(self):
        self.data = []
        self.stills_pk_counter = 0

    def add_movie(self, movie_dict):
        movie_dict.pop('stills')
        self.data.append(
            asdict(MovieFixture(
                pk=movie_dict.pop('id'),
                fields=movie_dict
            ))
        )

    def add_person(self, person_dict):
        self.data.append(
            asdict(PersonFixture(
                pk=person_dict.pop('id'),
                fields=person_dict
            ))
        )

    def add_countries(self, items):
        for name, pk in items:
            self.data.append(
                asdict(CountryFixture(
                    pk=pk,
                    fields={'name': name}
                ))
            )

    def add_genres(self, items):
        for name, pk in items:
            self.data.append(
                asdict(GenreFixture(
                    pk=pk,
                    fields={'name': name}
                ))
            )

    def add_stills(self, movie_id, stills: list):
        for i in range(len(stills)):
            self.stills_pk_counter += 1
            self.data.append(
                asdict(MovieStillFixture(
                    pk=self.stills_pk_counter,
                    fields={
                        'movie': movie_id,
                        'image': f"movies/{movie_id}/stills/still_{i + 1}.jpg",
                    }
                ))
            )


class FixturesCreator:
    def __init__(self):
        self._movies = file_m.movies_data_json.read(Movie)
        self._persons = file_m.persons_data_json.read(Person)
        self._fixtures = FixturesCollector()

        countries_counter, genres_counter = count(start=1), count(start=1)
        self._country_pk_dict = defaultdict(lambda: next(countries_counter))
        self._genre_pk_dict = defaultdict(lambda: next(genres_counter))
        self._person_url_pk_dict = {}

    def run(self):
        self._get_persons_fixtures()
        self._get_movies_fixtures()
        return self._fixtures.data

    def _get_persons_fixtures(self):
        for person in self._persons:
            person.image = f"persons/{person.id}/photo.webp"

            if person.motherland:
                person.motherland = self._country_pk_dict[person.motherland]

            self._person_url_pk_dict[person.kp_url] = person.id

            self._fixtures.add_person(asdict(person))

    def _get_movies_fixtures(self):
        for movie in self._movies:
            movie.image = f"movies/{movie.id}/poster.webp"

            self._fixtures.add_stills(movie.id, movie.stills)

            movie.countries = [self._country_pk_dict[c] for c in movie.countries]

            movie.genres = [self._genre_pk_dict[g] for g in movie.genres]

            for role_key in ('actors', 'directors', 'writers'):
                setattr(
                    movie,
                    role_key,
                    [self._person_url_pk_dict[person_url] for person_url in getattr(movie, role_key)]
                )

            self._fixtures.add_movie(asdict(movie))

        self._fixtures.add_countries(self._country_pk_dict.items())
        self._fixtures.add_genres(self._genre_pk_dict.items())
