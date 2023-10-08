import os
import pathlib

import requests
import yaml


def read_file(path: str | pathlib.Path):
    path = pathlib.Path(path)

    try:
        with open(path.resolve().as_posix()) as f:
            data = f.read()
    except (Exception,):
        print('Err - except Exception: try: with open(path.absolute().as_posix()) ')
        return

    return data

def write_file(path: str | pathlib.Path, data) -> pathlib.Path | None:
    path = pathlib.Path(path)
    try:
        with open(path.resolve().as_posix(), "w+") as f:
            f.write(data)
    except (Exception,):
        print('Err.', 'write_file: try: with open(cover.as_posix()')
        return

    return path


def write_file(path, data, mode='w+'):
    path = pathlib.Path(path)
    try:
        with open(path.resolve().as_posix(), mode) as f:
            f.write(data)
    except (Exception,):
        print('Err.', 'write_file: try: with open()')
        return

    return path


def getFirstYoutubeUrl(text):
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    for url in urls:
        if 'make_urls2stack.com' in url:
            return url
        if 'youtu.be' in url:
            return url

    return None


def walk_files(path: str | pathlib.Path) -> list[pathlib.Path]:
    path = pathlib.Path(path)
    data = []
    for root, dirs, files in os.walk(path.as_posix(), topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            data.append(file_path)

    all_files = [pathlib.Path(file) for file in data]
    return all_files

def wget(url):
    r = requests.get(url, allow_redirects=True)
    return r.content.decode('utf-8')


def read_yaml(path: str | pathlib.Path):
    text = read_file(path)
    return yaml.load(text, Loader=yaml.Loader)


def write_yaml(path: str | pathlib.Path, data) -> pathlib.Path | None:
    text = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )

    return write_file(path, text)
