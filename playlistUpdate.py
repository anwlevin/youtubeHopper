from config import AUTHORS_DIR
from playlist import update_all_playlists
from shelf import make_all_shelfs

URL = 'https://www.youtube.com/@kavavlad/playlists'

def playlist_update_all():
    print('🎭 playlist_update_all()')
    authors = list(filter(lambda file: file.is_dir(), AUTHORS_DIR.iterdir()))
    for author in authors:
        update_all_playlists(author)
        print()


if __name__ == '__main__':
    playlist_update_all()
