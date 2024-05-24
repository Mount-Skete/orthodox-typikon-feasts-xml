import math
import re
from datetime import datetime, timedelta

import apache_beam as beam
from apache_beam.io import fileio
from bs4 import BeautifulSoup
from bs4 import Tag

from BookTypes import BookDay, HymnType, Hymn, HymnSet, Event, StringUtils


class BookMapper(beam.DoFn):
    _BOOK_START_DATE = datetime(2019, 9, 1)  # SEP 1
    __debug = False

    def read_book(self, soup):
        last_day_index = 4 if self.__debug else 379
        skip_days = 0

        days: list[BookDay] = []
        for i in range(1, last_day_index):
            julian = datetime(2019, 9, 1) + timedelta(days=i - skip_days - 1)

            day = self.query_day(soup, julian, skip_days)

            if day is None:
                skip_days += 1
                continue

            if len(day.events) == 0:
                print(f'No events found for day {julian.isoformat()}')

            for event in day.events:
                print(event.header)

            days.append(day)

        return days

    @staticmethod
    def find_day_id(day_links):
        for link in day_links:
            if link['id'] and 'headertemplate' in link['id']:
                return link

        return None

    def query_day(self, soup, julian_day, skip_days) -> BookDay | None:
        day_index = self.calc_day_index_ref(julian_day) + skip_days
        day_book_ref = f'div[id*="c{day_index}_"]'
        day_links = soup.select(day_book_ref)
        day_link = self.find_day_id(day_links)

        if not day_link:
            raise Exception(f'Header template not found for {day_book_ref}')

        text_el = day_link.find_next_sibling('div', 'text')
        if text_el is None or 'text' not in text_el['class']:
            # Workaround for source bugs dayIndex === 55, 146, 156
            text_el = day_link.parent.find_next_sibling().select_one(':first-child')

            if not text_el or 'text' not in text_el.get('class', []):
                raise Exception(f'Text not found {day_book_ref}')

        el = text_el.select('.prp-pages-output')
        if len(el) == 0:
            print(f'Ignoring month index page {day_book_ref}')
            # raise Exception(f'Content element not found for {day_book_ref}')
            return None

        el = el[0]

        # Parallelize

        el = el.select('.heading')
        if len(el) == 0:
            print(f'Heading not found {day_book_ref}')
            return None

        el = el[0]

        # Print day name
        print(el.text.strip())

        el = el.find_next_sibling('hr')
        event_id = 1
        evs: list[Event] = []
        event, el = self.extract_event_content(el)
        event.id = self.gen_event_id(day_index, event_id)
        evs.append(event)

        while event is not None and el is not None:
            event, el = self.extract_event_content(el)

            if event is None or el is None:
                break

            event_id += 1
            event.id = self.gen_event_id(day_index, event_id)
            evs.append(event)

        return BookDay(events=evs,
                       julian=julian_day)

    def extract_event_content(self, el) -> (Event, Tag):
        if el is None:
            return None, None

        def match_caps_heading(tag):
            classes = tag.get('class', [])
            return 'heading' in classes and 'h-caps' in classes

        hr = el
        if not match_caps_heading(el):
            el = el.find_next_sibling(match_caps_heading)

        header = None
        # id=314 try find combined header
        if el is None:
            # pass
            print('Searching combined header')
            el = hr.find_next_sibling()
            if el is None:
                print('Header not found')
                return None, None
            header = self.extract_text(el)
        else:
            h1 = []
            while el is not None and el.get('class') and 'heading' in el.get('class'):
                h1.append(self.extract_text(el))
                el = el.find_next_sibling()

            header = ' '.join(h1)

        if header is None:
            return None, None

        texts = []
        while (el is not None
               and (el.name == 'p' or el.name == 'span' or el.name == 'hr' or
                    (el.name == 'div' and 'epigraph2' in el.get('class', [])) or
                    ('heading' in el.get('class', [])
                     and 'h-caps' not in el.get('class', [])
                     and 'h-razr' not in el.get('class', [])
                    )
                    or 'lives-div' in el.get('class', []))):
            text = self.extract_text(el)
            if text:
                texts.append(text)

            el = el.find_next_sibling()

        hymns = self.extract_hymns(header, texts)

        return Event(header=StringUtils.clean(header), content=texts, hymns=hymns, id=''), el

    def extract_text(self, el):
        if not el:
            return ''

        drops = el.select('.dropinitial')
        if len(drops) > 0:
            for drop in drops:
                a = drop.select_one('a img')
                if a and len(a.get('alt', [])) > 0:
                    letter = a.get('alt')
                    drop.replace_with(letter)

        chu_texts = el.select('span.ponomar')
        if len(chu_texts) > 0:
            for text in chu_texts:
                ch = text.get('title')
                text.replace_with(ch)

        sups = el.select('sup')
        if len(sups) > 0:
            for sup in sups:
                sup.clear()

        return StringUtils.clean(el.text)

    def extract_hymns(self, header: str, texts: list[str]) -> HymnSet | None:
        if not texts or len(texts) == 0:
            return None

        hymns: list[Hymn] = []
        for idx in range(len(texts)):
            text = texts[idx]
            # for idx, text in enumerate(texts):
            if (text.startswith('Кондак')
                    or text.startswith('Другий кондак')
                    or text.startswith('Ин кондак')
                    or text.startswith('Тропарь')
                    or text.startswith('Другий тропарь')
                    or text.startswith('Ин тропарь')):
                h_type = HymnType.Troparion

                if (text.startswith('Кондак')
                        or text.startswith('Другий кондак')
                        or text.startswith('Ин кондак')):
                    h_type = HymnType.Kontakion

                echo: int = 0
                if m := re.match(r'.*, глас (\d):', text):
                    echo = int(m.group(1))

                if echo == 0:
                    print(f'echo==0 source={text}')
                    #assert echo != 0

                hymns.append(Hymn(header=header,
                                  title=text,
                                  content=texts[idx + 1],
                                  type=h_type,
                                  echo=echo))

        return HymnSet(hymns=hymns, title=header)

    @staticmethod
    def days_between(date1: datetime, date2: datetime) -> int:
        return int(math.fabs((date1 - date2).days))

    def calc_day_index_ref(self, julian_day) -> int:
        day_index = self.days_between(self._BOOK_START_DATE, julian_day) + 1

        return day_index

    @staticmethod
    def gen_event_id(day_index, index):
        return f'ls-{day_index}-{index}'

    def process(self, element, **kwargs):
        soup = BeautifulSoup(element[1], 'lxml')

        days = self.read_book(soup)
        for day in days:
            yield day


class BookParser(beam.PTransform):
    def __init__(self, path: str):
        super().__init__()
        self.__path = path

    def expand(self, pcoll):
        result = (
                pcoll
                | fileio.MatchFiles(self.__path)
                | fileio.ReadMatches()
                | beam.Map(lambda x: (x.metadata.path, x.read_utf8()))
                | beam.ParDo(BookMapper())
                # | beam.Map(lambda x: print(x.events[0].header))
        )

        return result
