#!/usr/bin/env python
from config import STACK_CLIPS_DIR, DISCOVER_DIR, DISCOVER_URLS_CLIPS_TXT
from utils import write_file, read_file, walk_files

from pytube import YouTube


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


def make_urls2stack():
    print('🏓 make_urls2stack(): ')
    print()

    if not DISCOVER_DIR.exists():
        print('🛑 Err \t  not URLS_CLIPS_TXT.exists():')
        return

    all_files = walk_files(DISCOVER_DIR)
    urls_files = list(filter(lambda file: file.name == DISCOVER_URLS_CLIPS_TXT.name, all_files))

    clip_ids = []
    for url_file in urls_files:
        print('url_file: ', url_file)
        urls_clips_text = read_file(url_file)

        for clip_url in list(set(urls_clips_text.strip().split('\n'))):
            clip_id = get_clip_id_from_yt_url(clip_url)
            clip_ids.append(clip_id)
            print()

    clip_ids = list(set(clip_ids))
    if not STACK_CLIPS_DIR.exists():
        print('✂️', 'create STACK_CLIPS_DIR')
        STACK_CLIPS_DIR.mkdir(parents=True, exist_ok=True)

    for clip_id in clip_ids:
        path = STACK_CLIPS_DIR.joinpath(f'{clip_id}.txt')
        write_file(path, '')

    print()


if __name__ == '__main__':
    make_urls2stack()










