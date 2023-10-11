#!/usr/bin/env python
from author import get_author_channel_id
from config import DISCOVER_STORE_ALL_CHATS_DIR, DISCOVER_URLS_TXT_FILE, VALID_YOUTUBE_DOMAINS_SET, \
    TEMPLATE_AUTHOR_DIR_NAME, TEMPLATE_VIDEO_FILE_NAME, TEMPLATE_VIDEO_SHORT_URL, TEMPLATE_PLAYLIST_URL, \
    TEMPLATE_PLAYLIST_FILE_NAME, TEMPLATE_AUTHOR_WHOLE_CHANNEL_FILE_NAME
from parser import get_soup_html, get_var_data_of_soup
from author_playlist import get_playlist_id
from utils import read_file, write_yaml
from urllib.parse import urlparse
import pathlib

from config import AUTHORS_STORE_DIR
from utils import write_file, walk_files

from pytube import YouTube
import requests


def author_clip_init(author_url) -> pathlib.Path | None | bool:
    if len(url_parts := author_url.split('@')) < 2:
        print('🛑️ Err \t  len(url_parts) < 2:')
        return True

    if not (author_dir := AUTHORS_STORE_DIR.joinpath(url_parts[-1])).exists():
        print('♻️ \t  not author_dir.exists():')
        author_dir.mkdir(parents=True, exist_ok=True)

    return author_dir


def thumbnail_clip(thumbnail_url, author_dir, clip_slug) -> pathlib.Path | None:
    # print('🖼 thumbnail_clip')
    if not thumbnail_url:
        print('🛑️ Err \t not thumbnail_url:')
        return

    thumbnail_url = thumbnail_url.split('?')[0]

    ext_s = thumbnail_url.split('.')
    if len(ext_s) < 2:
        print('🛑️ Err \t len(ext_s) < 2:')
        return
    ext = ext_s[-1]

    r = requests.get(thumbnail_url, allow_redirects=True, stream=True)

    thumbnail_file = author_dir.joinpath(f'{clip_slug}-thumbnail.{ext}')
    return write_file(thumbnail_file, r.content, mode='wb+')


def get_yt_data(url):
    try:
        yt = YouTube(url)

    except Exception as e:
        print('🛑 Err \t Exception as e:')
        return

    if not yt:
        return

    return yt


def get_clip_id_from_yt_url(url):
    print('🎣', url)

    yt = get_yt_data(url)
    if not yt:
        print('🛑 Err \t not yt:')
        return

    clip_id = yt.vid_info['videoDetails']['videoId']
    if not clip_id:
        print('🛑 Err \t  not clip_id:')
        return

    print('🏈', clip_id)

    return clip_id


def get_username_out_author_url(url):
    if not (purl := urlparse(url)).path:
        return

    if len(path_parts := purl.path.split('/')) < 2:
        return

    if '@' not in (first_part := path_parts[1]):
        return

    if len(username_parts := first_part.split('@')) < 2:
        return

    username = username_parts[1]

    return username


def get_author_playlist_core_details(json_data):
    if not (header := json_data.get('header')):
        return

    if not (playlist_header_renderer := header.get('playlistHeaderRenderer')):
        return

    if not (owner_text := playlist_header_renderer.get('ownerText')):
        return

    if not (runs := owner_text.get('runs')):
        return

    if not (navigation_endpoint := runs[0].get('navigationEndpoint')):
        return

    if not (browse_endpoint := navigation_endpoint.get('browseEndpoint')):
        return

    context = dict()

    if browse_id := browse_endpoint.get('browseId'):
        context['id'] = browse_id

    if canonical_base_url := browse_endpoint.get('canonicalBaseUrl'):
        if '/@' in canonical_base_url:
            if username := canonical_base_url.split('/@')[1]:
                context['username'] = username

    return context


def get_author_playlist_id(json_data):
    if not (details := get_author_playlist_core_details(json_data)):
        return

    if not (id_author := details.get('id')):
        return

    return id_author


def get_author_playlist_username(json_data):
    if not (details := get_author_playlist_core_details(json_data)):
        print('details: ', details)
        return

    if not (username := details.get('username')):
        print('username: ', username)
        return

    return username


def process_video_url(url):
    print('⚙️🧩 Video Process', url, '\n')

    if not (soup := get_soup_html(url)):
        print('⛔️ not soup:')
        return

    if not (id_meta := soup.find("meta", itemprop="identifier")):
        print('⛔️ not id_meta:')
        return

    if not (id_video := id_meta.get('content')):
        print('⛔️  not id_video ')
        return

    if not (author_span := soup.find("span", itemprop="author")):
        print('⛔️ not author_span:')
        return

    if not (author_link := author_span.find("link")):
        print('⛔️ not author_link:')
        return

    if not (author_url := author_link.get('href')):
        print('⛔️ not author_url:')
        return

    if not (username_author := get_username_out_author_url(author_url)):
        print('⛔️ not username_author:')
        return

    author_dir_name = TEMPLATE_AUTHOR_DIR_NAME.substitute(username_author=username_author)
    if not (author_dir := AUTHORS_STORE_DIR.joinpath(author_dir_name)).exists():
        author_dir.mkdir(parents=True, exist_ok=True)

    if (video_file := author_dir.joinpath(TEMPLATE_VIDEO_FILE_NAME.substitute(video_id=id_video))).exists():
        print('⛔️ author_dir.exists():')
        return

    write_yaml(
        video_file,
        {
            'url': TEMPLATE_VIDEO_SHORT_URL.substitute(video_id=id_video),
            'id': id_video,
            'author_username': username_author,
        })


def process_playlist_url(url):
    print('⚙️⛺️ Playlist Process', url, '\n')

    if not (id_playlist := get_playlist_id(url)):
        return

    classic_url = TEMPLATE_PLAYLIST_URL.substitute(playlist_id=id_playlist)

    if not (soup := get_soup_html(classic_url)):
        return

    if not(json_data := get_var_data_of_soup(soup)):
        return

    if not (username_author := get_author_playlist_username(json_data)):
        return

    author_dir_name = TEMPLATE_AUTHOR_DIR_NAME.substitute(username_author=username_author)
    if not (author_dir := AUTHORS_STORE_DIR.joinpath(author_dir_name)).exists():
        author_dir.mkdir(parents=True, exist_ok=True)

    if (playlist_file := author_dir.joinpath(TEMPLATE_PLAYLIST_FILE_NAME.substitute(playlist_id=id_playlist))).exists():
        print('!⛔️ playlist_file.exists()::')
        return

    write_yaml(
        playlist_file,
        {
            'url': classic_url,
            'id': id_playlist,
            'author_username': username_author,
        })


def process_channel_url(url):
    print('⚙️🏭 Channel Process', url, '\n')

    username_author = get_username_out_author_url(url)

    author_dir_name = TEMPLATE_AUTHOR_DIR_NAME.substitute(username_author=username_author)
    if not (author_dir := AUTHORS_STORE_DIR.joinpath(author_dir_name)).exists():
        author_dir.mkdir(parents=True, exist_ok=True)

    if not (soup := get_soup_html(url)):
        return

    if not(json_data := get_var_data_of_soup(soup)):
        return

    if not (id_author := get_author_channel_id(json_data)):
        return
    whole_channel_file = TEMPLATE_AUTHOR_WHOLE_CHANNEL_FILE_NAME.substitute(author_id=id_author)
    if (channel_author_file := author_dir.joinpath(whole_channel_file)).exists():
        print('!⛔️ TEMPLATE_AUTHOR_ABOUT_FILE_NAME)).exists()')
        return

    write_yaml(
        channel_author_file, {
            'url': url,
            'id': id_author,
            'author_username': username_author,
        })


def process_yt_link_to_store(url):
    print('🛒 Move URL to Store: ', url)

    purl = urlparse(url)
    if purl.netloc not in VALID_YOUTUBE_DOMAINS_SET:
        return

    if '/playlist' in purl.path and 'list' in purl.query:
        process_playlist_url(url)
        return

    if '/watch' in purl.path or 'youtu.be' in purl.netloc:
        process_video_url(url)
        return

    if '@' in purl.path:
        process_channel_url(url)
        return

    print('⭕️ No Parsed URL')


def make_all_urls2store():
    print('🏓 Make All Urls 2 Store()')

    if not DISCOVER_STORE_ALL_CHATS_DIR.exists():
        print('🛑 Err \t  not URLS_CLIPS_TXT.exists():')
        return

    if not AUTHORS_STORE_DIR.exists():
        AUTHORS_STORE_DIR.mkdir(parents=True, exist_ok=True)

    urls_files = list(filter(
        lambda file: file.name == DISCOVER_URLS_TXT_FILE.name, walk_files(DISCOVER_STORE_ALL_CHATS_DIR)))

    for url_file in urls_files:
        print('📁 URL File: ', url_file)
        print()

        if not (urls_clips_text := read_file(url_file)):
            continue

        for yt_url in list(set(urls_clips_text.strip().split('\n'))):
            process_yt_link_to_store(yt_url)
            print()

    print()
    print()
    print()


if __name__ == '__main__':
    make_all_urls2store()
