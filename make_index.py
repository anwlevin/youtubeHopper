#!/usr/bin/env python

from string import Template
import telegram
import yaml
from jinja2 import Environment, FileSystemLoader
from urlextract import URLExtract

import config
from utils import read_file, write_file, read_yaml


def text_preprocessing(text_html):
    text_html = str(text_html)

    if urls := URLExtract().find_urls(text_html):
        for url in urls:
            text_html = text_html.replace(url, f'<a href="{url}">{url}</a>')

    text_html = text_html.replace('\n', '<br>\n')

    return text_html


def render_forward_post_content(message: telegram.Message, data: dict):
    print('🛍 Forward')
    print('Message: ')
    print(message)
    print('===========')
    print()
    print()

    contents = []

    forward_chat = ''
    if hasattr(message, 'forward_from_chat'):
        if hasattr(message.forward_from_chat, 'title'):
            forward_chat += f'<strong>{message.forward_from_chat.title}</strong>'

        if hasattr(message.forward_from_chat, 'username'):
            forward_chat += f'<small>({message.forward_from_chat.username})</small>'

        if hasattr(message.forward_from_chat, 'id'):
            forward_chat += f' <small>[{message.forward_from_chat.id}]</small>'

    contents.append(f'<h5>{forward_chat}</h5>')

    if hasattr(message, 'forward_date'):
        contents.append(f'<p>{message.forward_date}</p>')

    contents.append(f'TEXT')
    contents.append('==========')
    contents.append(text_preprocessing(data.get('text_html')))

    content = '<br>'.join(contents)

    forward_templ = '''
    <div class="border border-primary ml-2 pl-3" 
        style="
            border-right: none!important;
            margin-left: .5rem;
            padding-left: 1rem;
            border-bottom: none!important;
            border-top: none!important;
            border-width: 1px!important;">
            $content
            </div>
            '''

    content = Template(forward_templ).substitute(content=content)
    return content


def get_index_playlists(author):
    print('🦬 get_index_playlists()')
    playlists = sorted(list(filter(
        lambda file: file.name.startswith('playlist-') and file.name.endswith('.yml'),
        author.iterdir())), reverse=True)
    pls = []
    all_videos = []
    for playlist in playlists:
        print(playlist)
        data = read_yaml(playlist)
        if not data.get('title'):
            continue
        videos = [author.joinpath(video) for video in data.get('videos')]
        all_videos += videos
        videos_context = get_context_videos(videos)
        context = dict({
                'url': data.get('url'),
                'title': data.get('title'),
                'videos': videos_context,
        })
        pls.append(context)

    return pls, all_videos


def get_context_videos(videos):
    all_videos_context = []
    for clip in videos:
        print('📮 Clip: ', clip.name)

        text_clip = read_file(clip)
        yaml_clip = yaml.load(text_clip, Loader=yaml.Loader)

        data_clip = yaml_clip

        context = dict()

        if not data_clip.get('title'):
            continue

        context['title'] = data_clip['title']
        context['date'] = data_clip['publish_date']
        context['url'] = data_clip['url']

        # clip_url = data_clip['url']
        clip_description = data_clip['description']
        context['description'] = f'''
            <p>
                {data_clip['publish_date']}
            </p>
            <p>
                {clip_description}
            </p>
        '''

        context['thumbnail'] = data_clip['thumbnail']

        all_videos_context.append(context)

    return all_videos_context


def make_index_one_author(author):
    print('🧿 make_index_one_author(): ', author.name)

    playlists, playlists_all_videos = get_index_playlists(author)

    playlists_all_videos = list(set(playlists_all_videos))

    videos = sorted(
        list(filter(lambda file: file.name.startswith('video-') and file.name.endswith('.yml'), author.iterdir())),
        reverse=True)

    videos = list(filter(lambda video: video not in playlists_all_videos, videos))

    clips_context = get_context_videos(videos)

    clips_context.sort(key=lambda clip_one: clip_one['date'], reverse=True)

    author_text = read_file(author.joinpath('about.yml'))
    author_data = yaml.load(author_text, Loader=yaml.Loader)
    author_data['username'] = author.name

    template = Environment(loader=FileSystemLoader("templates")).get_template("grid-cards-clips.html")
    write_file(author.joinpath('index.html'), template.render({
        'title': f'{author.name} | Index',
        'author': author_data,
        'clips': clips_context,
        'playlists': playlists
    }))


def make_all_index_authors():
    print('💎️ make_all_index_authors()')

    if not config.AUTHORS_STORE_DIR.exists():
        print('🚫 not config.AUTHORS_DIR.exists:')
        return

    author_dirs = sorted(list(filter(lambda file: file.is_dir(), config.AUTHORS_STORE_DIR.iterdir())), reverse=True)
    for author_dir in author_dirs:
        make_index_one_author(author_dir)

    print()
    print('💎️ make All Index (): ')
    authors_context = []

    for author_dir in author_dirs:
        author_data = read_yaml(author_dir.joinpath('about.yml'))
        author_data['username'] = author_dir.name
        author_data['thumbnail'] = author_dir.name + '/' + author_data['thumbnail']
        author_data['href'] = author_dir.name
        authors_context.append(author_data)

    authors_context.sort(key=lambda author: author['title'])

    template = Environment(loader=FileSystemLoader("templates")).get_template("index-authors-all.html")
    write_file(config.AUTHORS_STORE_DIR.joinpath('index.html'), template.render({
        'title': f'Index of the Authors',
        'authors': authors_context}))


if __name__ == '__main__':
    make_all_index_authors()
