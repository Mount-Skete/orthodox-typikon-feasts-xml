import os
import xml.etree.ElementTree as ET

import apache_beam as beam
from apache_beam.io import fileio

from BookTypes import BookDay, HymnType


class BookXmlMapper(beam.DoFn):
    def save_day(self, book_day: BookDay):
        events = ET.Element('feasts', {
            'julian': book_day.julian.isoformat(),
        })
        for book_event in book_day.events:
            if len(book_event.header.strip()) == 0:
                print(f'Skipping event with empty header {book_event.id}')
                continue

            event = ET.SubElement(events, 'feast')

            event.set('id', book_event.id)

            # Refs helper
            # refs = ET.SubElement(event, 'refs')
            # ref = ET.SubElement(refs, 'ref')
            # ref.set('id', book_event.id)

            title = ET.SubElement(event, 'title')
            title_ru = ET.SubElement(title, 'ru')
            title_ru.text = book_event.header

            date_el = ET.SubElement(event, 'date')
            date_jul = ET.SubElement(date_el, 'julian')
            date_jul.text = f'{book_day.julian.month:02}-{book_day.julian.day:02}'

            if book_event.hymns and book_event.hymns.hymns and len(book_event.hymns.hymns) > 0:
                hymns = ET.SubElement(event, 'hymns')
                for hymn in book_event.hymns.hymns:
                    hmn = ET.SubElement(hymns, 'hymn', {
                        'type': 'troparion' if hymn.type == HymnType.Troparion else 'kontakion',
                        'echo': str(hymn.echo)
                    })

                    title = ET.SubElement(hmn, 'title')
                    title_ru = ET.SubElement(title, 'ru')
                    title_ru.text = hymn.title

                    h_content = ET.SubElement(hmn, 'content')
                    h_content_ru = ET.SubElement(h_content, 'ru')
                    h_content_ru.text = hymn.content

            # if self.__save_content:
            if True:
                content = ET.SubElement(event, 'content')

                content_title = ET.SubElement(content, 'title')
                content_title_ru = ET.SubElement(content_title, 'ru')
                content_title_ru.text = book_event.header

                content_text = ET.SubElement(content, 'text')
                content_text_ru = ET.SubElement(content_text, 'ru')

                for text in book_event.content:
                    txt = ET.SubElement(content_text_ru, 'p')
                    txt.text = text

        tree = ET.ElementTree(events)
        ET.indent(tree)

        return ET.tostring(tree.getroot(), encoding='unicode', xml_declaration=True)

    def process(self, element, **kwargs):
        yield self.save_day(element)


class BookXmlWriter(beam.PTransform):
    def __init__(self, path: str):
        super().__init__()
        self.__path = path

    @staticmethod
    def destination_naming(item):
        julian = ET.XML(item).find('feast/date/julian').text
        return julian.replace('-', '/')

    @staticmethod
    def single_file_naming(window, pane, shard_index, total_shards, compression, destination):
        prefix = str(destination)
        return f'{prefix}.xml'

    @staticmethod
    def ensure_output(path):
        for i in range(1, 12):
            out_path = f'{path}/{i:02}'
            if not os.path.exists(out_path):
                os.makedirs(out_path)

    def expand(self, pcoll):
        self.ensure_output(self.__path)

        result = (
            pcoll
            | beam.ParDo(BookXmlMapper())
            | fileio.WriteToFiles(
                self.__path,
                destination=self.destination_naming,
                file_naming=self.single_file_naming,
                sink=fileio.TextSink),
        )

        return result
