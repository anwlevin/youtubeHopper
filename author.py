from author_whole_channel import get_all_channel_videos
from config import TEMPLATE_VIDEO_FILE_NAME, TEMPLATE_VIDEO_SHORT_URL
from parser import get_author_info, download_thumbnail
from author_playlist import filter_playlist_yml_files, update_playlist
from utils import write_yaml
from author_video import update_video, filter_video_yml_files


def get_author_channel_core_details(json_data):
    if not (header := json_data.get('header')):
        return

    if not (c4TabbedHeaderRenderer := header.get('c4TabbedHeaderRenderer')):
        print('header')
        print(header)
        return

    context = dict()

    if channelId := c4TabbedHeaderRenderer.get('channelId'):
        context['id'] = channelId

    if navigationEndpoint := c4TabbedHeaderRenderer.get('navigationEndpoint'):
        if commandMetadata := navigationEndpoint.get('commandMetadata'):
            if webCommandMetadata := commandMetadata.get('commandMetadata'):
                if url_username := webCommandMetadata.get('commandMetadata'):
                    if '/@' in url_username:
                        if username := url_username.split('/@')[1]:
                            context['username'] = username

    return context


def get_author_channel_id(json_data):
    if not (details := get_author_channel_core_details(json_data)):
        return

    if not (id_author := details.get('id')):
        return

    return id_author


def get_author_channel_username(json_data):
    if not (details := get_author_channel_core_details(json_data)):
        print('details: ', details)
        return

    if not (username := details.get('username')):
        print('username: ', username)
        return

    return username


def check_channel_yml_exist(author_dir):
    files = author_dir.iterdir()
    channel_files = list(filter(lambda file: file.name.startswith('channel-') and file.name.endswith('.yml'), files))
    if not channel_files:
        return

    return True


def get_youtube_author_url(author_username):
    return f'https://www.youtube.com/@{author_username}'


def update_author_about(author_dir):
    author_url = get_youtube_author_url(author_username=author_dir.name)

    data = get_author_info(author_url)

    thumbnail = download_thumbnail(
        data.get('thumbnail_url'),
        author_dir.joinpath('about-thumbnail.jpg'))

    write_yaml(author_dir.joinpath('about.yml'), {
        'url': author_url,
        'id': data.get('id'),
        'title': data.get('title'),
        'thumbnail_url': data.get('thumbnail_url'),
        'thumbnail': thumbnail.relative_to(author_dir).as_posix(),
        'description': 'Description',
    })


def update_all_single_author(author_dir):
    print('🌽 Single Author Update: ', author_dir.name)

    update_author_about(author_dir)

    if check_channel_yml_exist(author_dir):
        print('🐿 WHOLE CHANNEL UPDATE: ')
        print('Skip ... ')

        author_url_videos = f'https://www.youtube.com/@{author_dir.name}/videos'
        video_ids = get_all_channel_videos(author_url_videos)
        for id_video in video_ids:
            video_file_name = TEMPLATE_VIDEO_FILE_NAME.substitute(video_id=id_video)
            if (video_file := author_dir.joinpath(video_file_name)).exists():
                print('⛔️ video_file.exists():')
                continue

            write_yaml(
                video_file, {
                    'url': TEMPLATE_VIDEO_SHORT_URL.substitute(video_id=id_video),
                    'id': id_video,
                    'author_username': author_dir.name})

        # get shelf s

        # get playlists

    for playlist_file in filter_playlist_yml_files(author_dir.iterdir()):
        update_playlist(playlist_file)

    for video_file in filter_video_yml_files(author_dir.iterdir()):
        update_video(video_file)
