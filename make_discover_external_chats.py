#!/usr/bin/env python

from config import DISCOVER_STORE_ALL_CHATS_DIR, DISCOVER_CHATS, \
    DISCOVER_LAST_POST_FILENAME_TXT, DISCOVER_URLS_TXT_FILE, \
    TEMPLATE_DISCOVER_FOLDER_NAME
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


def get_undiscovered_posts(posts_all_text, last_post_filename):
    if not last_post_filename:
        return posts_all_text.split('\n')

    splitted_posts_groups = posts_all_text.split(last_post_filename)

    if len(splitted_posts_groups) < 2:
        return []

    if len(splitted_posts_groups[1]) < 4:
        print('🧩 No changes')
        return []

    undiscovered_posts = splitted_posts_groups[1].strip().split('\n')
    return undiscovered_posts


def discover_one_external_chat(chat):
    print('🥎 Discover One External chat()')
    if not chat.get('name') or not chat.get('url_index') or not chat.get('url_store'):
        return

    discover_chat_dit_name = TEMPLATE_DISCOVER_FOLDER_NAME.substitute(chat_name=chat.get('name'))
    discover_chat = DISCOVER_STORE_ALL_CHATS_DIR.joinpath(discover_chat_dit_name)
    if not discover_chat.exists():
        discover_chat.mkdir(parents=True, exist_ok=True)

    last_checked_post = get_last_discover_post(discover_chat.joinpath(DISCOVER_LAST_POST_FILENAME_TXT))

    raw_text_all_posts = wget(chat.get('url_index')).strip()

    posts = get_undiscovered_posts(raw_text_all_posts, last_checked_post)

    union_yt_url_set = []
    for post_filename in posts:
        union_yt_url_set += get_all_youtube_urls_from_external_url(f'{chat.get("url_store")}/{post_filename}')
        print()

    union_yt_url_set = list(set(union_yt_url_set))
    print('🛍 Combined New Youtube Urls: ')
    [print(url) for url in union_yt_url_set]

    write_file(discover_chat.joinpath(DISCOVER_LAST_POST_FILENAME_TXT), str(posts[-1]))

    write_file(discover_chat.joinpath(DISCOVER_URLS_TXT_FILE), '\n'.join(union_yt_url_set))


def discover_all_external_telegram_store_chats_make():
    print('🔮 Discover External Telegram Chats make() \n')

    for chat in DISCOVER_CHATS:
        discover_one_external_chat(chat)

        print()


if __name__ == '__main__':
    discover_all_external_telegram_store_chats_make()
