import json
import pathlib

import yaml

from config import AUTHORS_DIR, STACK_CLIPS_DIR
from utils import write_file, walk_files, read_file

from parseData import get_video_info
from pytube import YouTube
import requests


def author_clip_init(author_url) -> pathlib.Path | None | bool:
    url_parts = author_url.split('@')
    if len(url_parts) < 2:
        print('🛑️ Err \t  len(url_parts) < 2:')
        return True

    author_dir = AUTHORS_DIR.joinpath(url_parts[-1])
    if not author_dir.exists():
        print('♻️ \t  not author_dir.exists():')
        author_dir.mkdir(parents=True, exist_ok=True)

    return author_dir


def thumbnail_clip(thumbnail_url, author_dir, clip_slug) -> pathlib.Path | None:
    #print('🖼 thumbnail_clip')
    if not thumbnail_url:
        print('🛑️ Err \t not thumbnail_url:')
        return

    thumbnail_url = thumbnail_url.split('?')[0]

    exts = thumbnail_url.split('.')
    if len(exts) < 2:
        print('🛑️ Err \t len(exts) < 2:')
        return
    ext = exts[-1]

    r = requests.get(thumbnail_url, allow_redirects=True, stream=True)

    thumbnail_file = author_dir.joinpath(f'{clip_slug}-thumbnail.{ext}')
    return write_file(thumbnail_file, r.content, mode='wb+')


def process_one_clip(clip_id):
    print('⛺️ ', f'processOneClip: \t {clip_id}')

    walk_clips = walk_files(AUTHORS_DIR)
    clip_find_tag = f'video-{clip_id}'
    if clip_exist := list(filter(lambda clip: clip_find_tag in clip.name, walk_clips)):
        print('🗽 Yet Exist', '\n')
        return

    clip_url = f'https://youtu.be/{clip_id}'

    data_first = get_video_info(clip_url)

    author_dir = author_clip_init(data_first['channel_url'])
    if not author_dir:
        print('🛑 Err \t  with author_dir')
        return

    data_second = YouTube(clip_url)
    context = dict({
        'title': data_second.title,
        'publish_date': data_second.publish_date,
        'lengthSeconds': data_second.length,

        'url': clip_url,

        'description': data_first['description'],

        'channel_id': data_second.channel_id,
        'author': data_second.author,
        'thumbnail_url': data_second.thumbnail_url,
    })

    clip_slug = f'video-{clip_id}'

    if thumbnail_path := thumbnail_clip(context['thumbnail_url'], author_dir, clip_slug):
        context['thumbnail'] = thumbnail_path.name

    video_text = yaml.dump(
        context,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    write_file(author_dir.joinpath(f'{clip_slug}.yml'), video_text)
    print()


from pytube import YouTube, Channel

import scrapetube


def channleProcessing():
    print('🎿 channleProcessing():')
    print()

    #yt = YouTube('https://www.youtube.com/watch?v=5kx5VUd8l2U')
    #print(yt.channel_url)

    channel_url = 'https://www.youtube.com/@AndriiBaumeister'
    channel_url = 'https://www.youtube.com/@kavavlad'
    channel_url = 'https://www.youtube.com/channel/UCwmN5lmbQUkwi-_oXPfh3SQ'

    videos = scrapetube.get_channel("UCwmN5lmbQUkwi-_oXPfh3SQ")
    #yt_channel = YouTube(channel_url)
    #print(yt_channel.get)
    v_ids = []
    for ic, clip in enumerate(videos):
        #print(clip)
        yaml_clip = yaml.dump(clip)
        v_ids.append(clip['videoId'])
        #print(yaml_clip)
        #print('\n\n\n')

    write_file('vids-list.txt', '\n'.join(v_ids))

    return

    if not AUTHORS_DIR.exists():
        AUTHORS_DIR.mkdir(parents=True, exist_ok=True)

    if not STACK_CLIPS_DIR.exists():
        print('if not CLIPS_DIR.exists():')
        return

    clips_txt = STACK_CLIPS_DIR.iterdir()

    clips = [clip_txt.stem for clip_txt in clips_txt]
    for clip in clips:
        process_one_clip(clip)


def belo_kofe():
    text = read_file('vids-list.txt')
    vids = text.split('\n')
    for vid in vids:
        write_file(STACK_CLIPS_DIR.joinpath(f'{vid}.txt'), '')


if __name__ == '__main__':
    #channleProcessing()
    belo_kofe()
