from urllib.parse import urlparse, parse_qsl, parse_qs
from bs4 import BeautifulSoup

from config import TEMPLATE_SHELF_FILE_NAME
from parser import get_selenium_html
from author_playlist import get_playlist_id
from utils import write_yaml


def get_all_channel_videos(url):

    html = get_selenium_html(url)

    soup = BeautifulSoup(html, "html.parser")

    contents = soup.find('div', {'id': 'contents'})

    render_all = contents.findAll('ytd-rich-item-renderer')

    video_ids = []
    for idx, render in enumerate(render_all):
        print(idx, len(render_all))
        a_title = render.find('a', {'id': 'video-title-link'})
        url = a_title.get('href')

        purl = urlparse(url)
        query_dict = parse_qs(purl.query)
        if 'v' not in query_dict:
            continue
        id_video = query_dict.get('v')[0]

        video_ids.append(id_video)

    return video_ids


def get_shelf_id(url):
    url_parse = urlparse(url)
    query_dict = dict(parse_qsl(url_parse.query))
    if 'shelf_id' not in query_dict:
        return

    return query_dict.get('shelf_id')


def get_playlists_shelf_page(url):
    print('🍄 Shelf Page - Get Playlists')

    html = get_selenium_html(url)
    soup = BeautifulSoup(html, "html.parser")

    if not (playlist_soup_renders := soup.find_all('ytd-grid-playlist-renderer')):
        return

    playlists_id_set = []
    for playlist_soup in playlist_soup_renders:
        if not (a_pl := playlist_soup.find('a', {"id": "video-title"})):
            continue

        if not (id_pl := get_playlist_id(a_pl.get('href'))):
            continue

        playlists_id_set.append(id_pl)

    return playlists_id_set


def get_all_shelf_set_meta(author_url):
    print('💦 Get All Shelf s Set 2ver:', author_url)
    """ if Title set == real shelf
    """

    html = get_selenium_html(author_url)
    soup = BeautifulSoup(html, "html.parser")

    if not (shelf_soup_s := soup.find_all('ytd-item-section-renderer')):
        return

    shelf_meta_set = []
    for i, shelf in enumerate(shelf_soup_s):

        if not (div_title_container := shelf.find('div', {"id": "title-container"})):
            continue

        if not (div_title_text := div_title_container.find('div', {"id": "title-text"})):
            continue

        a = div_title_text.find('a')
        span = div_title_text.find('span', {"id": "title"})

        shelf_meta_set.append({
            'id': get_shelf_id(a.get('href')),
            'title': span.text.strip(),
            'url': 'https://www.youtube.com' + a.get('href'),
        })

    return shelf_meta_set


def update_all_shelf_set(author_dir):
    author_url = f'https://www.youtube.com/@{author_dir.name}/playlists'

    common_playlists = get_playlists_shelf_page(author_url)

    for shelf in get_all_shelf_set_meta(author_url):
        print('🍩 Shelf: ', shelf.get('url'), shelf.get('title'), '\n')

        playlists_shelf_files = get_playlists_shelf_page(shelf.get('url'))

        id_shelf = get_shelf_id(shelf.get('url'))
        if str(id_shelf) == '0':
            print('skip --- Shelf: Created ==> ')
            continue

        print('🍟 Write YAML \t', id_shelf, '\n')
        write_yaml(
            author_dir.joinpath(TEMPLATE_SHELF_FILE_NAME.substitute(shelf_id=id_shelf)), {
                'id': id_shelf,
                'url': shelf.get('url'),
                'title': shelf.get('title'),
                'playlists': playlists_shelf_files})

        common_playlists += playlists_shelf_files

    return common_playlists
