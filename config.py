#!/usr/bin/env python

import pathlib
from string import Template

DISCOVER_CHATS = [
    {
        'name': 'chat-1560011833',
        'url_index': 'https://anwlevin.github.io/hopperTelegram/store/chat-1560011833/index.txt',
        'url_store': 'https://anwlevin.github.io/hopperTelegram/store/chat-1560011833/',
    },
]

DISCOVER_STORE_ALL_CHATS_DIR = pathlib.Path('discover')

DISCOVER_URLS_TXT_FILE = pathlib.Path('urls.txt')

DISCOVER_LAST_POST_FILENAME_TXT = pathlib.Path('last.txt')

AUTHORS_STORE_DIR = pathlib.Path('youtube')

TEMPLATE_DISCOVER_FOLDER_NAME = Template("discover-$chat_name")

VALID_YOUTUBE_DOMAINS_SET = ['youtube.com', 'youtu.be', 'www.youtube.com', 'www.youtu.be']

TEMPLATE_AUTHOR_DIR_NAME = Template("$username_author")

TEMPLATE_VIDEO_FILE_NAME = Template("video-$video_id.yml")

TEMPLATE_VIDEO_SHORT_URL = Template("https://youtu.be/$video_id")

TEMPLATE_PLAYLIST_URL = Template('https://www.youtube.com/playlist?list=$playlist_id')

TEMPLATE_PLAYLIST_FILE_NAME = Template("playlist-$playlist_id.yml")

TEMPLATE_AUTHOR_ABOUT_FILE_NAME = Template('about.yml').substitute()

TEMPLATE_AUTHOR_WHOLE_CHANNEL_FILE_NAME = Template("channel-$author_id.yml")

TEMPLATE_VIDEO_THUMBNAIL_FILE_NAME = Template("$video_file_stem-thumbnail.$ext_thumbnail")

TEMPLATE_SHELF_FILE_NAME = Template('shelf-$shelf_id.yml')
