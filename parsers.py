import re
from functools import cached_property

import bs4
from bs4 import BeautifulSoup

from config import config
from utils.url_manager import url_m


class BaseParser:
    def __init__(self, page):
        self._soup = BeautifulSoup(page, "lxml")

    def as_dict(self):
        d = {}
        for k, v in self.__class__.__dict__.items():
            if type(v) is property:
                d[k] = getattr(self, k)
        return d


class MovieListParser(BaseParser):
    @property
    def positions(self):
        return [elem.text for elem in self._soup.select('.styles_position__TDe4E')]

    @property
    def urns(self):
        return [elem.get('href') for elem in self._soup.select('.base-movie-main-info_link__YwtP1')]

    def as_dict(self):
        d = {}
        for pos, urn in zip(self.positions, self.urns):
            d[pos] = url_m.base + urn
        return d


class MovieParser(BaseParser):
    @property
    def rus_title(self):
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
        return int(self._about_table['Год производства'].text)

    @property
    def countries(self):
        return [a.text for a in self._about_table['Страна'].find_all('a')]

    @property
    def duration(self):
        return int(self._about_table['Время'].text.split(' ')[0])

    @property
    def tagline(self):
        t = self._about_table['Слоган'].text
        if t == '—':
            return None
        return t

    @property
    def genres(self):
        return [a.text for a in self._about_table['Жанр'].find_all('a')][:-1]

    @property
    def directors(self):
        return self._extract_person_urls(self._about_table['Режиссер'])

    @property
    def writers(self):
        return self._extract_person_urls(self._about_table['Сценарий'])

    @property
    def actors(self):
        return self._extract_person_urls(self._soup.select('.styles_actors__wn_C4')[0])

    @property
    def synopsys(self):
        return self._soup.select('.styles_paragraph__wEGPz')[0].text.replace('\xa0', ' ')

    @property
    def image(self):
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

    @cached_property
    def _rating_section(self):
        return self._soup.find(class_='styles_ratingValue__UO6Zl styles_rootLSize__X4aDt')

    @cached_property
    def _about_table(self):
        required_fields = ('Год производства', 'Страна', 'Жанр', 'Слоган', 'Режиссер', 'Сценарий', 'Время')

        table = self._soup.select('div[data-test-id="encyclopedic-table"]')[0]
        table_rows = table.find_all(class_='styles_row__da_RK')

        d = {}
        for row in table_rows:
            key = row.find(class_='styles_title__b1HVo').text
            if key in required_fields:
                d[key] = row.find(class_='styles_value__g6yP4')
        return d

    @staticmethod
    def _extract_person_urls(tag: bs4.Tag):
        return [url_m.person_number_to_url(n)
                for n in re.findall(r'name/(\d+)/', str(tag))]


class MovieStillsParser(BaseParser):
    @property
    def images_urls(self):
        return [
            'https:' + elem.get('href')
            for elem in self._soup.select('.styles_download__kQ848')[:config.still_num]
        ]


class PersonParser(BaseParser):
    @property
    def rus_name(self):
        return self._soup.select('.styles_primaryName__2Zu1T')[0].text

    @property
    def orig_name(self):
        try:
            return self._soup.select('.styles_secondaryName__MpB48')[0].text
        except IndexError:
            return None

    @property
    def birth_date(self):
        try:
            date_obj = ' '.join(
                [a.text for a in self._about_table['Дата рождения'].find_all('a')[:2]]
            ).split(' ')
            return self._d_m_y_format(date_obj)
        except (IndexError, ValueError):
            return None

    @property
    def death_date(self):
        date_elem = self._about_table.get('Дата смерти')
        if date_elem:
            try:
                d = date_elem.text.split('•')[0].split(' ')
                date_obj = [d[0], d[1][:-1], d[2]]
                return self._d_m_y_format(date_obj)
            except (IndexError, ValueError):
                return None
        return None

    @property
    def motherland(self):
        try:
            motherland = self._about_table['Место рождения'].find_all('a')[-1].text
        except (TypeError, IndexError):
            return None

        words = []
        for word in motherland.split(' '):
            if not word.isupper():
                word = word.title()
            words.append(word)
        return ' '.join(words)

    @property
    def image(self):
        if self._soup.select('.styles_root__DZigd')[0].get('srcset'):
            return 'https:' + self._soup.select('.styles_root__DZigd')[0].get('src')
        return False

    @cached_property
    def _about_table(self):
        required_fields = ('Дата рождения', 'Место рождения', 'Дата смерти')

        table = self._soup.select('.styles_table__p64a3')[0]
        table_rows = table.find_all(class_='styles_rowDark__ucbcz')

        d = {}
        for row in table_rows:
            key = row.find(class_='styles_title__b1HVo').text
            if key in required_fields:
                d[key] = row.find(class_='styles_value__g6yP4')
        return d

    @staticmethod
    def _d_m_y_format(date_obj):
        months = [
            'января',
            'февраля',
            'марта',
            'апреля',
            'мая',
            'июня',
            'июля',
            'августа',
            'сентября',
            'октября',
            'ноября',
            'декабря',
        ]

        day, month, year = int(date_obj[0]), months.index(date_obj[1]) + 1, date_obj[2]
        return f'{day:02d}-{month:02d}-{year}'.strip()
