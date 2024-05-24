import locale
import math
from argparse import ArgumentParser
from timeit import default_timer as timer

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

from BookParser import BookParser
from BookXmlParser import BookXmlParser
from BookXmlWriter import BookXmlWriter

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, locale.locale_alias['ru'])

    parser = ArgumentParser()
    parser.add_argument("--parse-sources",
                        dest="parse_sources",
                        required=False,
                        action="store_true")
    args = parser.parse_args()

    full_src = "sources/lives-of-the-saints.html"
    short_src = "sources/lives-of-the-saints-short.html"
    output_path = '../../lives-of-the-saints-ru'

    start = timer()

    options = PipelineOptions(
        runner='DirectRunner',
        # direct_num_workers=0,
        direct_running_mode='in_memory'  # 'in_memory', 'multi_threading', 'multi_processing'
    )

    with beam.Pipeline(options=options) as p:
        if args.parse_sources:
            (
                p
                | BookParser(full_src)
                | BookXmlWriter(output_path)
            )

        (
            p
            | BookXmlParser(output_path)
            | beam.combiners.Count.Globally()
            | beam.Map(print)
        )

    elapsed = int(math.ceil(timer() - start))
    print(f'Processing time: {elapsed} seconds')
