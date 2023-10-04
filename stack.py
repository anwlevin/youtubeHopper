import pathlib

import yaml

from utils import write_file, walk_files

NOTES_ROOT = 'notes'


import pathlib
from parseData import get_video_info
from pytube import YouTube, extract, Channel
import requests

from string import Template
from slugify import slugify
from datetime import datetime


def preData(url):
    out = {}
    data = get_video_info(url)

    out['description'] = data['description']
    # print(data)

    yt = YouTube(url)
    out['title'] = yt.title

    out['thumbnail_url'] = yt.thumbnail_url

    out['id'] = yt.vid_info['videoDetails']['videoId']

    return out


def if_note_exist(video_id):
    path = pathlib.Path().absolute().parent.joinpath(NOTES_ROOT)

    for ff in path.iterdir():
        if video_id in ff.as_posix():
            return ff.name

    return False



template = Template(
'''
### $title



[$url]($url)


[$url_short]($url_short)


```
$description
```



![$thumbnail_path]($thumbnail_path)
'''
)

def wget(url, path):
    r = requests.get(url, allow_redirects=True, stream=True)
    write_file(path, r.content, mode='wb+')



def makeNote(url):
    print('URL: ', url)
    print()

    id0 = extract.video_id(url)

    if yet_note := if_note_exist(id0):
        print('🍎', 'Note yet Exists! Continue')
        print('\t', yet_note)
        print()
        return yet_note


    timestamp = str(int(datetime.now().timestamp()))
    # print(timestamp)

    data = preData(url)
    # print('Data: ', data)

    id = data['id']
    title = data['title']
    slug = slugify(title)

    name = f'{timestamp}_{slug:.32}_{id}'

    thumbnail_url = data['thumbnail_url']

    thumbnail_url = thumbnail_url.split('?')[0]
    # print(thumbnail_url)

    ext = thumbnail_url.split('.')[-1]

    new_thumb_name = f'{name}.{ext}'

    root = pathlib.Path().absolute().parent
    notes = root.joinpath(NOTES_ROOT)

    new_thumb_path = notes.joinpath(new_thumb_name)

    wget(thumbnail_url, new_thumb_path.as_posix())


    mapping = {
        'title': title,
        'url':  url,
        'url_short':  f'https://youtu.be/{id0}',
        'description': data['description'],
        'thumbnail_path': new_thumb_name
    }
    text = template.substitute(**mapping)
    # print(text)

    md_name = f'{name}.md'

    write_file(notes.joinpath(md_name), text)





YOUTUBE_STORE = pathlib.Path('youtube')
CLIPS_DIR = pathlib.Path('clips')

def authorClipInit(author_url):
    url_parts = author_url.split('@')
    if len(url_parts) < 2:
        print('🛑️ Err \t  len(url_parts) < 2:')
        return True

    author_dir = YOUTUBE_STORE.joinpath(url_parts[-1])
    if not author_dir.exists():
        print('♻️ \t  not author_dir.exists():')
        author_dir.mkdir(parents=True, exist_ok=True)

    return author_dir


def thumbnailCip(thumbnail_url, author_dir, clip_slug):
    if not thumbnail_url:
        return

    thumbnail_url = thumbnail_url.split('?')[0]

    exts = thumbnail_url.split('.')
    if len(exts) < 2:
        return
    ext = exts[-1]

    r = requests.get(thumbnail_url, allow_redirects=True, stream=True)

    thumbnail_file = author_dir.joinpath(f'{clip_slug}-thumbnail.{ext}')
    write_file(thumbnail_file, r.content, mode='wb+')


def processOneClip(clip_id):
    print('⛺️ ', f'processOneClip: \t {clip_id}')

    walk_clips = walk_files(YOUTUBE_STORE)
    clip_find_tag = f'video-{clip_id}'
    if clip_exist := list(filter(lambda clip: clip_find_tag in clip.name, walk_clips)):
        print('🗽 Yet Exist', '\n')
        return

    clip_url = f'https://youtu.be/{clip_id}'

    data_first = get_video_info(clip_url)

    author_dir = authorClipInit(data_first['channel_url'])
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

    if thumbnail_path := thumbnailCip(context['thumbnail_url'], author_dir, clip_slug):
        context['thumbnail'] = thumbnail_path

    video_text = yaml.dump(
        context,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    write_file(author_dir.joinpath(f'{clip_slug}.yml'), video_text)
    print()


def stack():
    print('🎿 stack(): \n')
    print()

    if not YOUTUBE_STORE.exists():
        YOUTUBE_STORE.mkdir(parents=True, exist_ok=True)

    if not CLIPS_DIR.exists():
        print('if not CLIPS_DIR.exists():')
        return

    clips_txt = CLIPS_DIR.iterdir()

    clips = [clip_txt.stem for clip_txt in clips_txt]
    for clip in clips:
        processOneClip(clip)




if __name__ == '__main__':
    stack()
