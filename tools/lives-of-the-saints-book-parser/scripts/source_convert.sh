#!/bin/bash

DIR="$(realpath "$(dirname "$0")")"
#pandoc -f epub -t html4 \
#       -o "${DIR}/../sources/lives-of-the-saints.html" \
#       "${DIR}/../sources/lives-of-the-saints.epub" \
#       --standalone \
#       --embed-resources

pandoc -f epub -t html4 \
       -o "${DIR}/../sources/lives-of-the-saints.html" \
       "${DIR}/../sources/lives-of-the-saints.epub"
