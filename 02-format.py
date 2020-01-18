"""Formatter

Transforms the songs.csv data set into a single text file
suitable for fine-tuning a GPT2 model. The format is as follows:

SOURCE - Movie Name or other source
TITLE: Insert title here

Lyrics
Lyrics
Lyrics
---

"""
#!/usr/bin/env python

import csv
import sys

CSV_IN = 'songs.csv'
SEP = ','
TEXT_OUT = 'songs.txt'

def main():
    with open(TEXT_OUT, 'w') as text_file:
        with open(CSV_IN, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=SEP, quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                text_file.write('SOURCE - {}\n'.format(row[0]))
                text_file.write('TITLE: {}\n'.format(row[1]))
                text_file.write('{}---\n\n'.format(row[2]))
                


if __name__ == '__main__':
    sys.exit(main())
