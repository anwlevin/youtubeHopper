#!/usr/bin/env python

import requests
from utils import write_file, read_file
import pathlib
import yaml
from urlextract import URLExtract

lookingSites = [
    'https://anwlevin.github.io/hopperTelegram/store/chat-1560011833/index.txt'
]


def wget(url):
    r = requests.get(url, allow_redirects=True)
    return r.content.decode('utf-8')


def get_youtube_urls(url):
    print('🍩', url)
    raw = wget(url)
    post_yaml = yaml.load(raw, Loader=yaml.Loader)
    if not post_yaml.get('data'):
        return

    data = post_yaml.get('data')

    if not data.get('text_html'):
        return

    text_html = data.get('text_html')
    print(text_html)
    print()

    y_urls = []
    if urls := URLExtract().find_urls(text_html):
        for url in urls:
            if 'youtube.com' in url or 'youtu.be' in url:
                y_urls.append(url)

    return y_urls



divider = 'post-170.yml'

divider = 'post-183.yml'

LAST_POST_TXT = pathlib.Path('last.txt')


def check_one_chat(url):
    print('🥎 check_one_chat()')
    last_post = None
    if LAST_POST_TXT.exists():
        last_post_text = read_file(LAST_POST_TXT).strip()
        if len(last_post_text) > 4 and 'post-' in last_post_text:
            last_post = last_post_text

    content = wget(url).strip()

    posts = content.split('\n')
    if last_post:
        parts = content.split(last_post)

        if len(parts) < 2:
            return

        if len(parts[1]) < 4:
            print('🧩 No changes')
            return

        print(f'>>{parts[1]}<<')
        posts = parts[1].strip().split('\n')

    print()
    print('Posts: ')
    print(posts)


    root_url = '/'.join(url.split('/')[:-1])
    print(root_url)
    print()

    youtube_urls = []
    for post_filename in posts:
        post_url = '/'.join([root_url, post_filename])
        y_urls = get_youtube_urls(post_url)
        if y_urls:
            youtube_urls += y_urls

    last_post = posts[-1]
    write_file('last.txt', str(last_post))

    print('🥎🥎')
    print('youtube_urls: ')
    print(youtube_urls)

    youtube_urls = list(set(youtube_urls))

    YOUTUBE_TXT = pathlib.Path('urls.txt')
    y_exist = []
    if YOUTUBE_TXT.exists():
        y_text = read_file(YOUTUBE_TXT)
        y_exist = y_text.strip().split('\n')

    y_save = []
    for n_url in  youtube_urls:
        if n_url in y_exist:
            continue
        y_save.append(n_url)

    print()
    print('y_save: ')
    print(y_save)
    write_file(YOUTUBE_TXT, '\n'.join(y_exist+y_save))


def check_updates():
    print('🍎', 'check_updates(): ')
    print()

    for chat_site in lookingSites:
        check_one_chat(chat_site)
    print('🍎🍎')



if __name__ == '__main__':
    print('🏀', 'main.py')

    check_updates()










