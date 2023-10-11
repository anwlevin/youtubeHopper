
from urllib.parse import urlparse, parse_qs
from pytube import Playlist
from config import TEMPLATE_VIDEO_FILE_NAME, TEMPLATE_VIDEO_SHORT_URL
from utils import write_yaml, read_yaml


def filter_playlist_yml_files(files):
    return list(filter(lambda file: file.name.startswith('playlist-') and file.name.endswith('.yml'), files))


def get_playlist_id(url):
    url_parse = urlparse(url)
    query_dict = parse_qs(url_parse.query)
    if 'list' not in query_dict:
        return

    return query_dict.get('list')[0]


def update_playlist(playlist_file):
    print('🥦 Playlist Update: ', playlist_file)

    data = read_yaml(playlist_file)

    if not data.get('url'):
        return

    yt_playlist = Playlist(data.get('url'))

    try:
        title = yt_playlist.title
    except Exception as e:
        title = 'Title Error'

    data['title'] = title

    try:
        description = yt_playlist.description
    except Exception as e:
        description = 'Description Error'
    data['description'] = description

    try:
        yt_playlist_videos = yt_playlist.videos
    except Exception as e:
        yt_playlist_videos = []

    video_files = []
    for yt_video in yt_playlist_videos:
        vide_filename = TEMPLATE_VIDEO_FILE_NAME.substitute(video_id=yt_video.video_id)
        video_file = playlist_file.parent.joinpath(vide_filename)
        if video_file.exists():
            continue

        write_yaml(video_file, {'url': TEMPLATE_VIDEO_SHORT_URL.substitute(video_id=yt_video.video_id)})

        video_files.append(video_file.name)

    data['videos'] = video_files

    write_yaml(playlist_file, data)
