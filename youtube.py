#!/usr/bin/env python

import requests
from utils import write_file, read_file
import pathlib
import yaml
from urlextract import URLExtract


from pytube import YouTube

YOUTUBE_TXT = pathlib.Path('urls.txt')


CLIPS_DIR = pathlib.Path('clips')
def parse_youtube(url):
    print('🎣 ', url)

    yt = None
    try:
        yt = YouTube(url)
    except Exception as e:
        pass

    if not yt:
        return

    yt_id = yt.vid_info['videoDetails']['videoId']

    print('🏈', yt_id)

    if not CLIPS_DIR.exists():
        CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    movie_stack = CLIPS_DIR.joinpath(f'{yt_id}.txt')
    if movie_stack.exists():
        return

    write_file(movie_stack, '')


def youtube():
    print('🏓 youtube(): ')
    print()
    if not YOUTUBE_TXT.exists():
        return

    urls_text = read_file(YOUTUBE_TXT)
    urls = urls_text.strip().split('\n')

    urls = list(set(urls))
    for url in urls:
        parse_youtube(url)


    print('🍎')



if __name__ == '__main__':
    youtube()










