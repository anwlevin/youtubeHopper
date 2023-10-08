from config import AUTHORS_DIR
from shelf import make_all_shelfs


def shelf_update_all():
    print('🎭 shelf_update_all()')
    authors = list(filter(lambda file: file.is_dir(), AUTHORS_DIR.iterdir()))
    for author in authors:
        make_all_shelfs(author)
        print()


if __name__ == '__main__':
    shelf_update_all()
