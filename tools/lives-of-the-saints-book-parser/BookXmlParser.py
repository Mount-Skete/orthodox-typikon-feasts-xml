import xml.etree.ElementTree as ET
from datetime import datetime

import apache_beam as beam
from apache_beam.io import fileio

from BookTypes import BookDay, Hymn, HymnSet, Event


class BookDayMapper(beam.DoFn):

    @staticmethod
    def read_day_xml(xml):
        day = ET.XML(xml)

        book_day = BookDay()
        book_day.julian = datetime.fromisoformat(day.get('julian'))

        events = []
        xml_events = day.findall('feast')
        for xml_event in xml_events:
            xml_texts = [txt.text for txt in xml_event.findall('content/p')]

            hymns = []
            xml_hymns = xml_event.findall('hymns/hymn')
            if len(xml_hymns) > 0:
                hymns = [Hymn.from_xml(el) for el in xml_hymns]

            header = xml_event.find('title/ru').text
            event = Event(
                id=xml_event.get('id'),
                header=header,
                content=xml_texts,
                hymns=HymnSet(hymns, title=header)
            )
            events.append(event)

        book_day.events = events

        return book_day

    def process(self, element, **kwargs):
        yield self.read_day_xml(element[1])


class BookXmlParser(beam.PTransform):
    def __init__(self, path: str):
        super().__init__()
        self.__path = path

    def expand(self, pcoll):
        result = (
                pcoll
                | fileio.MatchFiles(f'{self.__path}/*/*.xml')
                | fileio.ReadMatches()
                | beam.Map(lambda x: (x.metadata.path, x.read_utf8()))
                | beam.ParDo(BookDayMapper())
        )

        return result
