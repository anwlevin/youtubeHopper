#!/usr/bin/env python
import re
from string import Template

import telegram
import yaml
from jinja2 import Environment, FileSystemLoader
from urlextract import URLExtract

import config
from utils import read_file, write_file


def text_Preprocessing(text_html):
    text_html = str(text_html)
    #print('🦜', 'Preprocessing text: ')
    #print(text_html)
    #print('==============')

    if urls := URLExtract().find_urls(text_html):
        for url in urls:
            text_html = text_html.replace(url, f'<a href="{url}">{url}</a>')

    text_html = text_html.replace('\n', '<br>\n')

    return text_html





def renderForwardPostContent(message: telegram.Message, data: dict):
    print('🛍 Forward')
    print('Message: ')
    print(message)
    print('===========')
    print()
    print()

    contents = []

    forw_chat = ''
    if hasattr(message, 'forward_from_chat'):
        if hasattr(message.forward_from_chat, 'title'):
            forw_chat += f'<strong>{message.forward_from_chat.title}</strong>'

        if hasattr(message.forward_from_chat, 'username'):
            forw_chat += f'<small>({message.forward_from_chat.username})</small>'

        if hasattr(message.forward_from_chat, 'id'):
            forw_chat += f' <small>[{message.forward_from_chat.id}]</small>'

    contents.append(f'<h5>{forw_chat}</h5>')

    if hasattr(message, 'forward_date'):
        contents.append(f'<p>{message.forward_date}</p>')

    contents.append(f'TEXT')
    contents.append('==========')
    contents.append(text_Preprocessing(data.get('text_html')))

    content = '<br>'.join(contents)

    forw_templ = '''
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

    content = Template(forw_templ).substitute(content=content)

    return content

    template = Environment(loader=FileSystemLoader("templates")).get_template("forwardPostContent.html")
    return template.render(
        {'title': f'Post {message.message_id}',
         'date': message.date.__str__(),
         'content': content,
         })


def makeIndexOneAuthor(author_dir):
    print('🧿 makeIndexOneAuthor(): ', author_dir.name)

    clips = sorted(list(filter(lambda file: file.name.startswith('video-') and file.name.endswith('.yml'), author_dir.iterdir())), reverse=True)

    clips_context = []

    for clip in clips:
        print('📮 Clip: ', clip.name)

        text_clip = read_file(clip)
        yaml_clip = yaml.load(text_clip, Loader=yaml.Loader)

        data_clip = yaml_clip

        clip_context = dict()

        clip_context['title'] = data_clip['title']
        clip_context['date'] = data_clip['publish_date']
        clip_context['url'] = data_clip['url']

        clip_url = data_clip['url']
        clip_description = data_clip['description']
        clip_context['description'] = f'''
        <p>
            {data_clip['publish_date']}
            </p>
        <p>
            {clip_description}
            </p>
        '''

        clip_context['thumbnail'] = data_clip['thumbnail']

        clips_context.append(clip_context)

    clips_context.sort(key=lambda clip_one: clip_one['date'], reverse=True)

    author_text = read_file(author_dir.joinpath('about.yml'))
    author_data = yaml.load(author_text, Loader=yaml.Loader)
    author_data['username'] = author_dir.name

    template = Environment(loader=FileSystemLoader("templates")).get_template("grid-cards-clips.html")
    write_file(author_dir.joinpath('index.html'), template.render({
        'title': f'{author_dir.name} | Index',
        'author': author_data,
        'clips': clips_context,
    }))



def makeIndexAllChats():
    print('💎️ makeIndexAllChats(): ')

    if not config.AUTHORS_DIR.exists():
        print('🚫 not config.AUTHORS_DIR.exists:')
        return

    author_dirs = sorted(list(filter(lambda file: file.is_dir(), config.AUTHORS_DIR.iterdir())), reverse=True)
    for author_dir in author_dirs:
        makeIndexOneAuthor(author_dir)

    print()
    print('💎️ make All Index (): ')
    authors_context = []

    for author_dir in author_dirs:
        author_text = read_file(author_dir.joinpath('about.yml'))
        author_data = yaml.load(author_text, Loader=yaml.Loader)
        author_data['username'] = author_dir.name
        author_data['thumbnail'] = author_dir.name + '/' + author_data['thumbnail']
        author_data['href'] = author_dir.name
        authors_context.append(author_data)

    authors_context.sort(key=lambda author: author['title'])

    template = Environment(loader=FileSystemLoader("templates")).get_template("index-authors-all.html")
    write_file(config.AUTHORS_DIR.joinpath('index.html'), template.render({
        'title': f'Index of the Store',
        'authors': authors_context}))



if __name__ == '__main__':

    makeIndexAllChats()
