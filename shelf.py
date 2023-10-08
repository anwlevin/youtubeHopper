from urllib.parse import urlparse, parse_qsl

from bs4 import BeautifulSoup

from parser import get_recursively, get_soup_html, get_selenium_html
from parser_playlist import get_var_data_of_soup
from playlist import get_all_playlists_on_shelf_page
from utils import write_yaml


def get_all_shelf_endpoints_urls(author_url):
    print('💦 shelf_endpoints() ')
    """
    if Title set == real shelf
    """

    soup = get_soup_html(author_url)
    js_data = get_var_data_of_soup(soup)

    shelf_s = []

    channel_sub_menu_renderer_s = get_recursively(js_data, 'channelSubMenuRenderer')
    if not channel_sub_menu_renderer_s:
        return
    shelf_endpoints = channel_sub_menu_renderer_s[0].get('contentTypeSubMenuItems')

    endpoints_result = []
    for i, shelf in enumerate(shelf_endpoints):
        context = dict()

        context['title'] = ''
        context['url'] = shelf.get('endpoint').get('commandMetadata').get('webCommandMetadata').get('url')
        context['url'] = 'https://www.youtube.com' + context.get('url')

        if 'shelf' in context['url']:
            context['title'] = shelf.get('title')
            shelf_s.append(context)

        endpoints_result.append(context)

    return endpoints_result


def get_all_shelfs_2v(author_url):
    print('💦 get_all_shelfs_2v()', author_url)
    """
    if Title set == real shelf
    """

    html = get_selenium_html(author_url)
    soup = BeautifulSoup(html, "html.parser")

    shelf_soup_s = soup.find_all('ytd-item-section-renderer')
    if not shelf_soup_s:
        return

    shelf_s = []
    for i, shelf in enumerate(shelf_soup_s):
        div_title_container = shelf.find('div', {"id": "title-container"})
        if not div_title_container:
            continue

        div_title_text = div_title_container.find('div', {"id": "title-text"})
        if not div_title_text:
            continue

        a = div_title_text.find('a')
        span = div_title_text.find('span', {"id": "title"})

        shelf_s.append({
            'id': get_shelf_id(a.get('href')),
            'title': span.text.strip(),
            'url': 'https://www.youtube.com' + a.get('href'),
        })

    return shelf_s


def get_shelf_id(url):
    url_parse = urlparse(url)
    query_dict = dict(parse_qsl(url_parse.query))
    if 'shelf_id' not in query_dict:
        return

    return query_dict['shelf_id']


def make_all_shelfs(author):
    print('🌷 get_all_playlists(): ', author.name)

    author_url = f'https://www.youtube.com/@{author.name}/playlists'

    common_playlists = get_all_playlists_on_shelf_page(author, author_url)

    for shelf in get_all_shelfs_2v(author_url):
        print('🍩 Shelf: ', shelf.get('url'), shelf.get('title'), '\n')

        playlists_shelf_files = get_all_playlists_on_shelf_page(author, shelf.get('url'))

        id_shelf = get_shelf_id(shelf.get('url'))
        if str(id_shelf) == '0':
            print('skip --- Shelf: Created ==> ')
            continue

        print('🍟 Write YAML \t', id_shelf, '\n')
        write_yaml(
            author.joinpath(f'shelf-{id_shelf}.yml'),
            {
                'id': id_shelf,
                'url': shelf.get('url'),
                'title': shelf.get('title'),
                'playlists': playlists_shelf_files,
            }
        )
        print()
