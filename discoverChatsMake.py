#!/usr/bin/env python

from config import DISCOVER_DIR, DISCOVER_CHATS, DISCOVER_LAST_POST_TXT, DISCOVER_URLS_CLIPS_TXT
from utils import write_file, read_file, wget

import yaml
from urlextract import URLExtract


def get_all_youtube_urls_from_external_url(url):
    print('🍩', url)

    raw = wget(url)
    post_yaml = yaml.load(raw, Loader=yaml.Loader)
    if not post_yaml.get('data'):
        return

    data = post_yaml.get('data')

    if not data.get('text_html'):
        return

    text_html = data.get('text_html')

    target_urls = []
    if all_urls := URLExtract().find_urls(text_html):
        for url in all_urls:
            if 'youtube.com' in url or 'youtu.be' in url:
                target_urls.append(url)

    return target_urls


def get_last_discover_post(chat_discover_file):
    if not chat_discover_file.exists():
        return

    last_post_text = read_file(chat_discover_file).strip()

    if len(last_post_text) < 4:
        return

    if 'post-' not in last_post_text:
        return

    return last_post_text


def get_undiscovered_posts(posts_all_text, last_post):
    if not last_post:
        return posts_all_text.split('\n')

    splitted_parts_posts = posts_all_text.split(last_post)

    if len(splitted_parts_posts) < 2:
        return

    if len(splitted_parts_posts[1]) < 4:
        print('🧩 No changes')
        return

    return splitted_parts_posts[1].strip().split('\n')


def discover_one_chat(chat):
    print('🥎 discover_one_chat()')

    chat_name = chat['name']

    discover_chat = DISCOVER_DIR.joinpath(f'discover-{chat_name}')
    if not discover_chat.exists():
        discover_chat.mkdir(parents=True, exist_ok=True)

    discover_chat_last_post = discover_chat.joinpath(DISCOVER_LAST_POST_TXT)
    last_post = get_last_discover_post(discover_chat_last_post)

    posts_all_text = wget(chat['url']).strip()
    posts = get_undiscovered_posts(posts_all_text, last_post)

    if not posts:
        return

    base_chat_url = '/'.join(chat['url'].split('/')[:-1])
    print('base_chat_url:', base_chat_url, '\n')

    combined_youtube_urls = []
    for post_name in posts:
        post_url = base_chat_url + '/' + post_name
        urls_youtube_of_post = get_all_youtube_urls_from_external_url(post_url)
        if not urls_youtube_of_post:
            continue
        combined_youtube_urls += urls_youtube_of_post
        print()

    print('🛍 combined_youtube_urls: ')
    combined_youtube_urls = list(set(combined_youtube_urls))
    [print(url) for url in combined_youtube_urls]

    write_file(discover_chat_last_post, str(posts[-1]))

    discover_chat_urls = discover_chat.joinpath(DISCOVER_URLS_CLIPS_TXT)
    write_file(discover_chat_urls, '\n'.join(combined_youtube_urls))

    print()


def discover_make():
    print('🔮 discover_make()')
    print()

    for chat in DISCOVER_CHATS:
        discover_one_chat(chat)
        print()


if __name__ == '__main__':

    discover_make()








