
import pathlib
import yaml
from config import AUTHORS_STORE_DIR
from parser import get_soup_html, get_var_data_of_soup, get_recursively, get_video_info
from utils import write_file, walk_files
from pytube import YouTube


def author_clip_init(author_url) -> pathlib.Path | None | bool:
    url_parts = author_url.split('@')
    if len(url_parts) < 2:
        print('🛑️ Err \t  len(url_parts) < 2:')
        return True

    author_dir = AUTHORS_STORE_DIR.joinpath(url_parts[-1])
    if not author_dir.exists():
        print('♻️ \t  not author_dir.exists():')
        author_dir.mkdir(parents=True, exist_ok=True)

    return author_dir


def process_one_clip(clip_id):
    print('⛺️ ', f'processOneClip: \t {clip_id}')

    walk_clips = walk_files(AUTHORS_STORE_DIR)
    clip_find_tag = f'video-{clip_id}'
    if clip_exist := list(filter(lambda clip: clip_find_tag in clip.name, walk_clips)):
        print('🗽 Yet Exist', '\n')
        return

    if clip_exist:
        pass

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

    video_text = yaml.dump(
        context,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    write_file(author_dir.joinpath(f'{clip_slug}.yml'), video_text)
    print()


def get_all_shelf_endpoints_urls(author_url):
    print('💦 shelf_endpoints() ')
    """
    if Title set == real shelf
    """

    soup = get_soup_html(author_url)
    js_data = get_var_data_of_soup(soup)

    shelf_s = []

    if not (channel_sub_menu_renderer_s := get_recursively(js_data, 'channelSubMenuRenderer')):
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
