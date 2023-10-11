import pathlib
from pytube import YouTube
from config import TEMPLATE_VIDEO_THUMBNAIL_FILE_NAME
from parser import download_thumbnail
from utils import read_yaml, write_yaml


def filter_video_yml_files(files):
    return list(filter(lambda file: file.name.startswith('video-') and file.name.endswith('.yml'), files))


def update_video(video_file: pathlib.Path):
    print('🦜 Video Update: \t', video_file.name)

    video_data = read_yaml(video_file)

    if not video_data.get('url'):
        return

    if video_data.get('title'):
        return

    yt_data = YouTube(video_data.get('url'))

    if not (ext_thumbnail := yt_data.thumbnail_url.split('.')[-1]):
        return

    filename_thumbnail = TEMPLATE_VIDEO_THUMBNAIL_FILE_NAME.substitute(
        video_file_stem=video_file.stem,
        ext_thumbnail=ext_thumbnail)
    if not (thumbnail := video_file.parent.joinpath(filename_thumbnail)).exists():
        download_thumbnail(yt_data.thumbnail_url, thumbnail)

    write_yaml(video_file, {
        'url': video_data.get('url'),
        'id': video_data.get('id'),
        'author_username': video_data.get('author_username'),

        'title': yt_data.title,
        'publish_date': yt_data.publish_date,
        'lengthSeconds': yt_data.length,
        'description': 'description',
        'thumbnail': thumbnail.name,
        'thumbnail_url': yt_data.thumbnail_url,
    })
