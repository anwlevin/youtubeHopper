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


def makeIndexOneChat(chat):
    print('🧿 makeIndexOneChat(): ', chat.name)

    #chat_about = chat.joinpath('about.yml')
    #chat_about_text = read_file(chat_about)
    #chat_about_yml = yaml.load(chat_about_text, Loader=yaml.Loader)
    #chat_title = chat_about_yml.get('title')
    #chat_title_small = chat_about_yml.get('title_small')
    #chat_id = chat_about_yml.get('id')
    #index_title = f'{chat_title} (chat: {chat_id})'


    clips = sorted(list(filter(lambda file: file.name.startswith('video-') and file.name.endswith('.yml'), chat.iterdir())), reverse=True)

    clips_context = []
    for clip in clips:
        print('📮 Clip: ', clip.name)

        text_clip = read_file(clip)
        yaml_clip = yaml.load(text_clip, Loader=yaml.Loader)

        data_clip = yaml_clip

        clip_context = dict()

        clip_context['title'] = data_clip['title']
        clip_context['date'] = data_clip['publish_date']

        text_html = data_clip['url']
        clip_url = data_clip['url']
        clip_description = data_clip['description']
        clip_context['text'] = f'''
        <p>
            <a href="{clip_url}">{clip_url}</a>
        </p>
        <p>{clip_description}</p>
        '''

        clip_context['photo'] = data_clip['thumbnail']

        clips_context.append(clip_context)

    template = Environment(loader=FileSystemLoader("templates")).get_template("index-chat-posts.html")
    write_file(chat.joinpath('index.html'), template.render({
        'title': f'{chat.name} | Index',
        'posts': clips_context,
        'chat': {
            'title': chat.name,
            'title_small': chat.name,
            'id': chat.name
        }
    }))



def makeIndexAllChats():
    print('💎️ makeIndexAllChats(): ')

    if not config.STORE_CLIPS.exists():
        print('🚫 not config.STORE_CLIPS.exists():')
        return

    chat_dirs = sorted(list(filter(lambda file: file.is_dir(), config.STORE_CLIPS.iterdir())), reverse=True)
    for chat in chat_dirs:
        makeIndexOneChat(chat)

    print()
    print('💎️ make All Index (): ')
    chats_context = []
    for chat in chat_dirs:
        #chat_about = chat.joinpath('about.yml')
        #chat_about_text = read_file(chat_about)
        #chat_about_yml = yaml.load(chat_about_text, Loader=yaml.Loader)
        #chat_title = chat_about_yml.get('title')
        #chat_title_small = chat_about_yml.get('title_small')
        #chat_id = chat_about_yml.get('id')

        chats_context.append({
            'href': chat.name,
            'title': chat.name,
            'title_small': chat.name,
            'id': chat.name,
        })

    template = Environment(loader=FileSystemLoader("templates")).get_template("index-store-chats.html")
    write_file(config.STORE_CLIPS.joinpath('index.html'), template.render({
        'title': f'Index of the Store',
        'chats': chats_context}))



if __name__ == '__main__':

    makeIndexAllChats()
