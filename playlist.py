import pathlib
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from pytube import Playlist

from parser import get_selenium_html
from utils import write_yaml, read_yaml


def get_playlist_id(url):
    url_parse = urlparse(url)
    query_dict = parse_qs(url_parse.query)
    if 'list' not in query_dict:
        return

    return query_dict.get('list')[0]


def get_all_playlists_on_shelf_page(author, url):
    print('🍄 get_all_playlists_on_shelf_page()')

    html = get_selenium_html(url)
    soup = BeautifulSoup(html, "html.parser")
    playlist_soup_renders = soup.find_all('ytd-grid-playlist-renderer')
    if not playlist_soup_renders:
        return

    playlists = []
    for playlist_soup in playlist_soup_renders:
        a_pl = playlist_soup.find('a', {"id": "video-title"})
        id_pl = get_playlist_id(a_pl.get('href'))
        if not id_pl:
            continue

        playlist = author.joinpath(f'playlist-{id_pl}.yml')
        if not playlist.exists():
            write_yaml(
                author.joinpath(f'playlist-{id_pl}.yml'),
                {
                    'url': f'https://www.youtube.com/playlist?list={id_pl}'
                }
            )

        playlists.append(playlist.name)

    return playlists


def update_all_playlists(author: pathlib.Path):
    print('🥗 Update playlists()')

    playlists = list(filter(lambda file: file.name.startswith('playlist-') and file.name.endswith('.yml'), author.iterdir()))

    for playlist in playlists:
        print('🥦', playlist)
        data_playlist = read_yaml(playlist)

        if not data_playlist.get('url'):
            continue

        print(data_playlist.get('url'))
        print()

        p = Playlist(data_playlist.get('url'))

        title = ''
        try:
            title = p.title
        except Exception as e:
            title = 'Ttile Error'
        data_playlist['title'] = title

        description = ''
        try:
            description = p.description
        except Exception as e:
            description = ''

        data_playlist['description'] = description

        video_filenames = []
        for vid in p.videos:
            print(vid.video_id)
            video_filename = f'video-{vid.video_id}.yml'
            video = author.joinpath(video_filename)
            url_video = f'https://youtu.be/{vid.video_id}'
            if not video.exists():
                write_yaml(video, {'url': url_video})

            video_filenames.append(video.name)
        data_playlist['videos'] = video_filenames
        write_yaml(playlist, data_playlist)

        print()

    return
