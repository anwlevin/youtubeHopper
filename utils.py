import pathlib

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


def getFirstYoutubeUrl(text):
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    for url in urls:
        if 'youtube.com' in url:
            return url
        if 'youtu.be' in url:
            return url

    return None
