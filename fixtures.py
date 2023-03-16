from collections import defaultdict
from dataclasses import dataclass, asdict
from itertools import count

from models import Movie, Person, Genre, Country, MovieStill
from utils.file_manager import file_m


@dataclass
class MovieFixture:
    pk: int
    fields: Movie
    model: str = 'movies.movie'


@dataclass
class PersonFixture:
    pk: int
    fields: Person
    model: str = 'movies.person'


@dataclass
class GenreFixture:
    pk: int
    fields: Genre
    model: str = 'movies.genre'


@dataclass
class CountryFixture:
    pk: int
    fields: Country
    model: str = 'movies.country'


@dataclass
class MovieStillFixture:
    pk: int
    fields: MovieStill
    model: str = 'movies.moviestill'


class FixturesCollector:
    def __init__(self):
        self.data = []
        self.stills_pk_counter = 0

    def add_movie(self, movie_id, data):
        self.data.append(
            asdict(MovieFixture(
                pk=movie_id,
                fields=Movie(**data)
            ))
        )

    def add_person(self, data):
        self.data.append(
            asdict(PersonFixture(
                pk=data.pop('person_id'),
                fields=Person(**data)
            ))
        )

    def add_countries(self, items):
        for name, pk in items:
            self.data.append(
                asdict(CountryFixture(
                    pk=pk,
                    fields=Country(
                        name=name
                    )
                ))
            )

    def add_genres(self, items):
        for name, pk in items:
            self.data.append(
                asdict(GenreFixture(
                    pk=pk,
                    fields=Genre(
                        name=name
                    )
                ))
            )

    def add_stills(self, movie_id, stills: list):
        for i in range(len(stills)):
            self.stills_pk_counter += 1
            self.data.append(
                asdict(MovieStillFixture(
                    pk=self.stills_pk_counter,
                    fields=MovieStill(
                        movie=movie_id,
                        image=f"movies/{movie_id}/stills/still_{i + 1}.jpg"
                    ),
                ))
            )


class FixturesCreator:
    def __init__(self):
        self._movies_data = file_m.movies_data_json.read()
        self._persons_data = file_m.persons_data_json.read()
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
        for person in self._persons_data:
            person['image'] = f"persons/{person['person_id']}/photo.webp"

            motherland = person['motherland']
            if motherland:
                person['motherland'] = self._country_pk_dict[motherland]

            self._person_url_pk_dict[person['kp_url']] = person['person_id']

            self._fixtures.add_person(person)

    def _get_movies_fixtures(self):
        for movie_id, movie in self._movies_data.items():
            self._movies_data[movie_id]['image'] = f"movies/{movie_id}/poster.webp"

            self._fixtures.add_stills(movie_id, self._movies_data[movie_id].pop('stills'))

            self._movies_data[movie_id]['countries'] = [
                self._country_pk_dict[c] for c in self._movies_data[movie_id]['countries']
            ]

            self._movies_data[movie_id]['genres'] = [
                self._genre_pk_dict[g] for g in self._movies_data[movie_id]['genres']
            ]

            for role_key in ('actors', 'directors', 'writers'):
                self._movies_data[movie_id][role_key] = \
                    [self._person_url_pk_dict[person_url] for person_url in movie[role_key]]

            self._fixtures.add_movie(movie_id, movie)

        self._fixtures.add_countries(self._country_pk_dict.items())
        self._fixtures.add_genres(self._genre_pk_dict.items())
