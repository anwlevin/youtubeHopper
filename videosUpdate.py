
import yaml

from config import AUTHORS_DIR
from stackMake import thumbnail_clip
from utils import write_file, walk_files, read_yaml

from parseData import get_video_info
from pytube import YouTube



def process_one_clip_ver2(author, clip_id):
    print('⛺️ ', f'processOneClip: \t {clip_id}')

    clip_url = f'https://youtu.be/{clip_id}'

    try:
        data_first = get_video_info(clip_url)
    except Exception as e:
        data_first = None

    if not data_first:
        return

    if not author:
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

    if thumbnail_path := thumbnail_clip(context['thumbnail_url'], author, clip_slug):
        context['thumbnail'] = thumbnail_path.name

    video_text = yaml.dump(
        context,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    write_file(author.joinpath(f'{clip_slug}.yml'), video_text)
    print()


def update_all_author_videos(author):
    print('🌽 update_all_author_videos(author): ', author.name)
    videos = list(filter(lambda file: file.name.startswith('video-') and file.name.endswith('.yml'), author.iterdir()))

    #if not author.name in ['AndriiBaumeister', ]:
    if not author.name in ['kavavlad', ]:
        return

    print(len(videos))

    for idx, video in enumerate(videos):
        print(idx, len(videos))
        video_data = read_yaml(video)
        if len(video_data) > 2:
            continue
        if not video_data.get('url'):
            continue

        print(video.name)
        video_id = video.name.split('video-')[1]
        video_id = video_id.split('.yml')[0]

        process_one_clip_ver2(author, video_id)

        print()


def allVideosUpdate():
    print('🎭 allVideosUpdate()')
    authors = list(filter(lambda file: file.is_dir(), AUTHORS_DIR.iterdir()))
    for author in authors:
        update_all_author_videos(author)
        print()




if __name__ == '__main__':
    allVideosUpdate()
