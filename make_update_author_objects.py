from author import update_all_single_author
from config import AUTHORS_STORE_DIR


def update_all_elements_in_author_store():
    print('🎭 Update All Elements in YML files Author Store')

    authors = list(filter(lambda file: file.is_dir(), AUTHORS_STORE_DIR.iterdir()))
    for author_dir in authors:
        update_all_single_author(author_dir)
        print()
        print()


if __name__ == '__main__':
    update_all_elements_in_author_store()
