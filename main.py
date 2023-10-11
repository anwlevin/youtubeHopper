#!/usr/bin/env python
from make_discover_external_chats import discover_all_external_telegram_store_chats_make
from make_discover_to_store import make_all_urls2store
from make_index import make_all_index_authors
from make_update_author_objects import update_all_elements_in_author_store


def main():
    discover_all_external_telegram_store_chats_make()
    make_all_urls2store()
    update_all_elements_in_author_store()
    make_all_index_authors()


if __name__ == '__main__':
    main()
