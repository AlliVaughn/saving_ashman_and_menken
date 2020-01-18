#!/usr/bin/env python

from bs4 import BeautifulSoup
from langdetect import detect
import urllib.request
import collections
import csv
import logging
import re
import sys

BASE_URL = 'https://www.allthelyrics.com'
FILTER_ELS = '/lyrics/pixar'
LANGS = ('en', )
CSV_OUT = 'songs_pixar.csv'
SEP = ','

# Python namedtuple
Song = collections.namedtuple('Song', 'album title lyrics')

logging.basicConfig(level=logging.DEBUG)


def validate_en(lyrics):
    """Validate that song lyrics are written in English

    Arguments:
        lyrics (str): Song lyrics

    Returns:
        bool: Whether the lyrics are English or not
    """

    l = detect(lyrics)
    logging.info('Language: {}'.format(l))
    if l in LANGS:
        return True
    else:
        return False


def get_lyrics_data(url):
    """Fetch and extract lyrics data from an all the lyrics URL

    Arguments:
        url (str): an AllTheLyrics song URL

    Returns: 
        Song: A named tuple containing song lyric data
    """
    source = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source, 'html.parser')
    title, album, lyrics = None, None, None

    # song title
    # get page title first...
    title = soup.title.string
    # then sanitize page title into song title
    title = re.sub('^Pixar – ', '', title)
    title = re.sub(' lyrics', '', title)
    logging.info('Title: {}'.format(title))

    # album
    for a in soup.find_all('div', class_='content-text-album'):
        album = a.text
        # strip leading string from album div text
        album = re.sub('Album: ', '', album)
    logging.info('Album {}'.format(album))

    # lyrics
    for d in soup.find_all('div', class_='content-text-inner'):
        lyrics_raw = d.text
        if validate_en(lyrics_raw):
            lyrics = lyrics_raw
            # Some songs lyrics are written (character)Lyric which will confuse the system. Add a space to fix this.
            lyrics = re.sub('\)', ') ', lyrics)
            lyrics = re.sub('[ ]{1,}', ' ', lyrics)
            # Some songs have character : lyric -OR- (character) : lyric. Drop leding space from colon character
            lyrics = re.sub(' :', ':', lyrics)
            # Some songs have [character:] lyric. Drop the internal colon character.
            lyrics = re.sub(':] ', '] ', lyrics)
            return Song(album, title, lyrics)
        else:
            raise ValueError('Non-English song')


def fetch_urls_from_index(url):
    """Fetch song links from an AllTheLyrics index URL
    
    Arguments:
        url (str): an AllTheLyrics index URL

    Returns: 
        list: A list of AllTheLyrics song URLs
    """
    urls = []
    source = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(source, 'html.parser')
    for t in soup.find_all('a'):
        href = t.get('href')
        # all lyrics pages start with /lyrics
        if href.startswith('/lyrics'):
            urls.append(BASE_URL + href)

    logging.info('Candidate URLs: {}'.format(len(urls)))
    return urls


def main():
    song_count = 0
    with open(CSV_OUT, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=SEP, quoting=csv.QUOTE_MINIMAL)
        for u in fetch_urls_from_index(BASE_URL + FILTER_ELS):
            try:
                song = get_lyrics_data(u)
                writer.writerow(list(song))
                song_count = song_count + 1
            except Exception:
                logging.exception('Skipped')

    logging.info('Songs extracted: {}'.format(song_count))


if __name__ == '__main__':
    sys.exit(main())
