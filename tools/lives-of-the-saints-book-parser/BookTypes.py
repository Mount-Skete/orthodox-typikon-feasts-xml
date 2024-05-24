import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class StringUtils:
    __rx = re.compile(r'\s+')

    @staticmethod
    def clean(text):
        clean = text.replace('\n', ' ')

        clean = StringUtils.__rx.sub(' ', text)
        clean = clean.replace(u'\u200e', ' ')  # LRM

        # Fix
        clean = clean.replace('\\Хар', 'Хар')

        return clean.strip()


class HymnType(Enum):
    Troparion = "Тропарь"
    Kontakion = "Кондак"


@dataclass
class Hymn:
    title: str
    content: str
    echo: Optional[int] = 0
    week_day: Optional[int] = 0

    header: Optional[str] = ''
    type: Optional[HymnType] = HymnType.Troparion

    @staticmethod
    def from_xml(item: ET.Element):
        # TODO: verify tag name

        type = item.attrib.get('type')
        h_type = HymnType.Troparion
        if type and type == 'kontakion':
            h_type = HymnType.Kontakion

        return Hymn(title=StringUtils.clean(item.find('title/ru').text),
                    content=StringUtils.clean(item.find('content/ru').text),
                    echo=int(item.attrib['echo']),
                    week_day=int(item.attrib['week_day']) if item.get('week_day') else 0,
                    type=h_type)


@dataclass
class HymnSet:
    hymns: list[Hymn]
    title: str


@dataclass
class Event:
    id: str
    header: str
    hymns: HymnSet

    content: list[str]
    is_special: bool = False


@dataclass
class BookDay:
    julian: datetime = Optional[datetime]
    events: list[Event] = field(default_factory=list)


@dataclass
class BookMonth:
    days: list[BookDay]

    def __init__(self):
        self.days = []
        for i in range(32):
            self.days.append(BookDay())
