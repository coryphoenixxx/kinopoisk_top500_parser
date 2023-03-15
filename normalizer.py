from dataclasses import asdict

from models import Genre, GenreFields, MovieStill, MovieStillFields, Country, CountryFields, Person, PersonFields, \
    Movie, MovieFields
from utils.file_manager import file_m


class Normalizer:
    def __init__(self):
        self._movies_data = file_m.movies_data_json.read()
        self._persons_data = file_m.persons_data_json.read()

        self._movie_stills_fixtures = []
        self._countries_fixtures = []
        self._genres_fixtures = []
        self._persons_fixtures = []
        self._movies_fixtures = []

    def create_fixtures(self):
        self.replace_images_urls()
        self.replace_countries()
        self.replace_genres()
        self.replace_persons()

        for data in self._persons_data:
            self._persons_fixtures.append(
                asdict(Person(
                    pk=data.pop('person_id'),
                    fields=PersonFields(**data)
                ))
            )

        for movie_id, data in self._movies_data.items():
            self._movies_fixtures.append(
                asdict(Movie(
                    pk=movie_id,
                    fields=MovieFields(**data)
                ))
            )

        result = []
        result.extend(self._movies_fixtures)
        result.extend(self._persons_fixtures)
        result.extend(self._genres_fixtures)
        result.extend(self._countries_fixtures)
        result.extend(self._movie_stills_fixtures)

        file_m.fixtures_json.write(result)

    def replace_persons(self):
        person_url_pk_dict = {}

        for data in self._persons_data:
            person_url_pk_dict[data['kp_url']] = data['person_id']

        for movie_id, data in self._movies_data.items():
            self._movies_data[movie_id]['actors'] = \
                [person_url_pk_dict[person_url] for person_url in data['actors']]
            self._movies_data[movie_id]['directors'] = \
                [person_url_pk_dict[person_url] for person_url in data['directors']]
            self._movies_data[movie_id]['writers'] = \
                [person_url_pk_dict[person_url] for person_url in data['writers']]

    def replace_genres(self):

        genres = set()
        for _, data in self._movies_data.items():
            genres.update(data['genres'])

        genre_pk_dict = {}
        for i, genre in enumerate(sorted(genres), start=1):
            genre_pk_dict[genre] = i

            self._genres_fixtures.append(
                asdict(Genre(
                    pk=i,
                    fields=GenreFields(
                        name=genre
                    )
                ))
            )

        for movie_id, data in self._movies_data.items():
            movie_genres_pk_list = []
            for genre in data['genres']:
                movie_genres_pk_list.append(genre_pk_dict[genre])
            self._movies_data[movie_id]['genres'] = movie_genres_pk_list

    def replace_countries(self):
        countries = set()

        for _, data in self._movies_data.items():
            countries.update(data['countries'])

        for data in self._persons_data:
            motherland = data['motherland']
            if motherland:
                countries.add(motherland)

        country_pk_dict = {}
        for i, country in enumerate(sorted(countries), start=1):
            country_pk_dict[country] = i

            self._countries_fixtures.append(
                asdict(Country(
                    pk=i,
                    fields=CountryFields(
                        name=country
                    )
                ))
            )

        for movie_id, data in self._movies_data.items():
            movie_countries_pk_list = []
            for country in data['countries']:
                movie_countries_pk_list.append(country_pk_dict[country])
            self._movies_data[movie_id]['countries'] = movie_countries_pk_list

        upd_persons_data = []
        for data in self._persons_data:
            motherland = data['motherland']
            if motherland:
                data['motherland'] = country_pk_dict[motherland]
            upd_persons_data.append(data)
        self._persons_data = upd_persons_data

    def replace_images_urls(self):
        stills_pk_counter = 0
        for movie_id, data in self._movies_data.items():
            self._movies_data[movie_id]['image'] = f"movies/{movie_id}/poster.webp"

            for j in range(len(data['stills'])):
                stills_pk_counter += 1

                self._movie_stills_fixtures.append(
                    asdict(MovieStill(
                        pk=stills_pk_counter,
                        fields=MovieStillFields(
                            movie=movie_id,
                            image=f"movies/{movie_id}/stills/still_{j + 1}.jpg"
                        ),
                    ))
                )

            self._movies_data[movie_id].pop('stills')

        upd_persons_data = []
        for data in self._persons_data:
            data['image'] = f"persons/{data['person_id']}/photo.webp"
            upd_persons_data.append(data)
        self._persons_data = upd_persons_data
