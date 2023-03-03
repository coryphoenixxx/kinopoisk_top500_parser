import re

import bs4
from bs4 import BeautifulSoup


class ProxyExtractor:
    def __init__(self, file):
        soup = BeautifulSoup(file, "lxml")
        self.movie = MovieExtractor(soup)
        self.person = PersonExtractor(soup)


class MovieExtractor:
    def __init__(self, soup):
        self._soup = soup
        self._table = None
        self._rating_section = None

    @property
    def urls(self):
        positions = self._soup.select('.styles_position__TDe4E')
        urls = self._soup.select('.base-movie-main-info_link__YwtP1')

        return positions, urls

    @property
    def rus_title(self):
        self._table = self._extract_about_table()  # TODO:
        self._extract_rating_section()

        rus_title = self._soup.select('.styles_title__65Zwx.styles_root__l9kHe.styles_root__5sqsd')[0].text
        return rus_title.split('(')[0].strip()

    @property
    def orig_title(self):
        try:
            orig_title = self._soup.select('.styles_originalTitle__JaNKM')[0].text
        except IndexError:
            return None

        return orig_title.strip()

    @property
    def year(self):
        return int(self._table['Год'].text)

    @property
    def countries(self):
        return [x.text for x in self._table['Страна'].find_all('a')]

    @property
    def duration(self):
        return int(self._table['Время'].text.split(' ')[0])

    @property
    def tagline(self):
        return self._table['Слоган'].text

    @property
    def genres(self):
        return [x.text for x in self._table['Жанр'].find_all('a')][:-1]

    @property
    def directors(self):
        return self._extract_person_number(self._table['Режиссер'])

    @property
    def writers(self):
        return self._extract_person_number(self._table['Сценарий'])

    @property
    def actors(self):
        a_tags = self._soup.select('.styles_actors__wn_C4')[0]
        return self._extract_person_number(a_tags)

    @property
    def description(self):
        return self._soup.select('.styles_paragraph__wEGPz')[0].text.replace('\xa0', ' ')

    @property
    def poster(self):
        return 'https:' + self._soup.select('.film-poster')[0].get('src')

    @property
    def kp_rating(self):
        return float(self._rating_section.find(class_='film-rating-value').text)

    @property
    def kp_count(self):
        return int(re.findall(
            r'[\d\s]+',
            self._rating_section.find(class_='styles_count__iOIwD').text
        )[0].replace(' ', ''))

    @property
    def imdb_rating(self):
        try:
            return float(re.findall(
                r'([\d.]+)',
                self._rating_section.find(class_='styles_valueSection__0Tcsy').text
            )[0])
        except AttributeError:
            return None

    @property
    def imdb_count(self):
        try:
            return int(re.findall(
                r'[\d\s]+',
                self._rating_section.find(class_='styles_count__89cAz').text
            )[0].replace(' ', ''))
        except AttributeError:
            return None

    def _extract_rating_section(self):
        self._rating_section = self._soup.find(class_='styles_ratingValue__UO6Zl styles_rootLSize__X4aDt')

    def _extract_about_table(self):
        required_fields = ('Год', 'Страна', 'Жанр', 'Слоган', 'Режиссер', 'Сценарий', 'Время')

        table = self._soup.select('div[data-test-id="encyclopedic-table"]')[0]

        table_rows = table.find_all(class_='styles_row__da_RK')

        d = {}
        for row in table_rows:
            key = row.find(class_='styles_title__b1HVo').text.split()[0]
            if key in required_fields:
                value = row.find_all(class_='styles_value__g6yP4')[0]
                d[key] = value
        return d

    @staticmethod
    def _extract_person_number(tag: bs4.Tag):
        return re.findall(r'name/(\d+)/', str(tag))


class PersonExtractor:
    def __init__(self, soup):
        self.soup = soup
