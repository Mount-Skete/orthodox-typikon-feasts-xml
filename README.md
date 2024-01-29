# Данные Православных Праздников и постов в XML

Проект содержит данные православных постов и праздников из Типикона,
книги "Житий святых" св. Димитрия Ростовского в формате XML.

Пример использования данных можно увидеть в проекте [Календаря Православных Праздников и Постов](https://github.com/Mount-Skete/liturgical-calendar).

# Структура проекта

## Праздники из Типикона

Праздники из Типикина находятся в папке `typikon-feasts-ru`. Праздники разделены по месяцам, даты указаны юлианском формате (старый стиль). Файл `feasts_movable.xml` содержит подвижные праздники, которые зависят от даты Пасхи. Некоторые праздники содержат также содержат тропари и кондаки.

Некоторые праздники содержат ссылку на данные из книги "Житий святых".

## Праздники из книги "Житий святых" св. Димитрия Ростовского

Праздники из книги "Житий святых" находятся в папке `lives-of-the-saints-ru`. Праздники разделены по месяцам и дням. Даты также указаны в старом стиле.

Данные праздников включают также и тексты из книги.

Источник: [Жития святых по изложению свт. Димитрия Ростовского](https://ru.wikisource.org/wiki/%D0%96%D0%B8%D1%82%D0%B8%D1%8F_%D1%81%D0%B2%D1%8F%D1%82%D1%8B%D1%85_%D0%BF%D0%BE_%D0%B8%D0%B7%D0%BB%D0%BE%D0%B6%D0%B5%D0%BD%D0%B8%D1%8E_%D1%81%D0%B2%D1%82._%D0%94%D0%B8%D0%BC%D0%B8%D1%82%D1%80%D0%B8%D1%8F_%D0%A0%D0%BE%D1%81%D1%82%D0%BE%D0%B2%D1%81%D0%BA%D0%BE%D0%B3%D0%BE)

### Формат данных

```xml
<feast id="" type="low" rank="ordinary">
  <refs>
    <ref id="ls-139-1" />
  </refs>
  <title>
    <ru>Святыя мученицы Татианы</ru>
  </title>
  <date>
    <julian>01-12</julian>
  </date>
  <hymns>
    <hymn type="kontakion" echo="4">
      <title>
        <ru>Кондак святыя, глас 4</ru>
      </title>
      <content>
        <ru>
          Светло во страдании твоем возсияла еси страстотерпице, от кровей твоих преиспещрена, и яко красная голубица, к небеси возлетела еси Татиано: темже моли присно за чтущия тя.
        </ru>
      </content>
    </hymn>
  </hymns>
</feast>
```

| Элемент | Описание |
|:-------:|---------------------------|
| `feast` | Базовый элемент. В данный момент поле `id` заполнено только в `lives-of-the-saints-ru` |
| `<ref id="ls-139-1" /> ` | Поле соддержит ссылку на `id` праздника из данных `lives-of-the-saints-ru`. |
| `title` | Содержит название праздника, как указано в источнике. |
| `<date><julian>01-12</julian></date>` | Дата праздника указана в старом стиле. Формат `месяц-день`. |
| `<date><easter days="+50"/></date>` | Дата подвижного праздника в расчете от даты Пасхи. В примере, дата Пасхи плюс 50 дней. |
| `<hymn type="kontakion" echo="4">` | Формат гимна праздника. Поле `type` указывает на тип: тропарь (`troparion`) или кондак (`kontakion`). Поле `echo` указывает на номер гласа. |
| `<hymn><title>` | Содержит название гимна как указано в источнике |
| `<hymn><content>` | Содержит текст гимна. |
| `<content><title>` | Содержит загаловок текста из книги "Житий святых". Только для данных из `lives-of-the-saints-ru` |
| `<content><text><p>` | Содержит текст из книги "Житий святых", разделенный на параграфы. Только для данных из `lives-of-the-saints-ru` |

## Православные посты

Данные православных постов находятся в папке `fasts-ru` и включают себя не только посты, но и праздничные дни когда пост отменяется.
Даты указаны юлианском формате (старый стиль).

## Формат данных
Данные разделены на два типа: описание поста и тип поста.

**Тип поста**
```xml
<fastType id="no-fast">
  <title>
    <ru>Поста нет</ru>
  </title>
</fastType>
```

| Элемент | Описание |
|:-------:|---------------------------|
| `fastType` | Базовый элемент. Содержит поле `id`, на которое ссылаются данные описания поста. |
| `title` | Содержит описание типа поста. |

**Описание поста**
```xml
<fast id="fast:marien" order="1">
  <title>
    <ru>Успенский пост</ru>
  </title>
  <start>
    <julian>08-01</julian>
  </start>
  <end>
    <julian>08-14</julian>
  </end>
  <schedule order="0">
    <day weekday="mon" fastType="no-oil"/>
    <day weekday="tue" fastType="no-oil"/>
    <day weekday="wed" fastType="dry"/>
    <day weekday="thu" fastType="no-oil"/>
    <day weekday="fri" fastType="dry"/>
    <day weekday="sat" fastType="oil"/>
    <day weekday="sun" fastType="oil"/>
  </schedule>
</fast>
```

| Элемент | Описание |
|:-------:|---------------------------|
| `fast` | Базовый элемент. Содержит поле `id` с коротким названием поста и поле `order`, указывающее на приоритет поста в случае пересекающихся постов. |
| `title` | Содержит навание поста. |
| `start`, `end` | Содержит даты начала и конца поста по юлианскому календарю или относительно даты Пасхи. |
| `schedule` | Содержит описание типов поста по дням, с указанием приоритета `order`. Пост может содержать несколько таких элентов. Также может содержать временные границы `start` и `end`. |
| `day` | Содержит описание типа поста на день. Поле `weekday` содержит день недели, а поле `fastType` содержит идентификатор типа поста, описаный выше. |

Пример обработки данных можно увидеть в проекте [Календаря Православных Праздников и Постов](https://github.com/Mount-Skete/liturgical-calendar).

# Инструменты

Папка `tools` содержит программы и скрипты для обработки данных.

## lives-of-the-saints-book-parser

Программа обрабатывает книгу "Житий святых" и создает `xml` документы с праздниками.

### Подготовка данных

Перед обработкой книгу нужно скачать в формате `epub` и преобразовать в `html` с помощью следующих скриптов.

```shell
./scripts/source_download.sh
./scripts/source_convert.sh
```

Конвертирование требует установки [Pandoc](https://pandoc.org).

### Запуск программы

```shell
python3 main.py --parse-sources
```

Данные будут сохранены в папке `output`.

# План работы

* Некоторые названия праздников и гимны содержат ошибки. Планируется их устранение используя другой источник и автоматическую корректировку.
* Планируется добавление перевода на церковно-славянский.

# Лицензия

Проект доступен по лицензии [MIT](LICENSE).
