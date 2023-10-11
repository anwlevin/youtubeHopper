import json
import pathlib
import re
import time
import requests
from selenium.webdriver import Keys, FirefoxOptions, Firefox
from selenium.webdriver.common.by import By
from utils import write_file
from requests_html import HTMLSession
from bs4 import BeautifulSoup


def download_file(url, target_path) -> pathlib.Path | None:
    if not url:
        return

    response = requests.get(url, allow_redirects=True, stream=True)
    if not response.content:
        return

    return write_file(target_path, response.content, mode='wb+')


def download_thumbnail(url, target_path) -> pathlib.Path | None:
    return download_file(url, target_path)


def get_selenium_html(url):
    options = FirefoxOptions()

    if True:
        options.add_argument("--headless")

    driver = Firefox(options=options)

    driver.get(url)

    # html_element = driver.find_element(By.TAG_NAME, "html")
    # html_element.send_keys(Keys.END)

    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    # driver.execute_script('window.scrollBy(0, 5000)')

    # time.sleep(10)

    if True:
        print('🐅🐆🐫🦒 Selenium: ', url)
        max_steps = 10
        for i in range(max_steps):
            print('\t', f'step {i} of {max_steps} ... ')
            height = driver.execute_script("return document.body.scrollHeight")
            time.sleep(2)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            if int(height) == 0:
                break

    source_data = driver.page_source

    driver.close()

    return source_data


def get_recursively(search_dict, field):
    fields_found = []

    for key, value in search_dict.items():

        if key == field:
            fields_found.append(value)

        elif isinstance(value, dict):
            results = get_recursively(value, field)
            for result in results:
                fields_found.append(result)

        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    more_results = get_recursively(item, field)
                    for another_result in more_results:
                        fields_found.append(another_result)

    return fields_found


def get_soup_html(url):
    try:
        session = HTMLSession()
        response = session.get(url)
    except Exception as e:
        print('⛔️  get_soup_html(url): Exception as e:')
        return

    soup = BeautifulSoup(response.html.html, "html.parser")
    return soup


def get_var_data_of_soup(soup):
    script_tags = soup.find_all('script')
    if not script_tags:
        return

    script_tags_filter = list(filter(lambda tag: 'ytInitialData' in tag.text, script_tags))
    if not script_tags_filter:
        return

    script_tag = script_tags_filter[0]

    re_search_result = re.search(r"var ytInitialData = (.*?);", script_tag.text)
    if not re_search_result:
        return
    try:
        js_data = json.loads(re_search_result.group(1))
    except Exception as e:
        return

    return js_data


def get_html_session(url):
    session = HTMLSession()
    response = session.get(url)
    return response.html.html


def get_soup_of_html_session(url):
    html = get_html_session(url)
    return BeautifulSoup(html, "html.parser")


def get_author_info(url):
    soup = get_soup_of_html_session(url)
    if not soup:
        return

    context = {
        'id': soup.find("meta", itemprop="identifier").get('content'),
        'title': soup.find("meta", itemprop="name").get('content'),
        'description': soup.find("meta", itemprop="description").get('content'),
        'thumbnail_url': soup.find("link", itemprop="thumbnailUrl").get('href'),
    }

    return context


def get_video_info(url):
    soup = get_soup_of_html_session(url)
    # open("index.html", "w").write(response.html.html)
    # initialize the result
    result = dict()
    # video title
    result["title"] = soup.find("meta", itemprop="name")['content']
    # video views
    result["views"] = soup.find("meta", itemprop="interactionCount")['content']
    # video description
    result["description"] = soup.find("meta", itemprop="description")['content']
    # date published
    result["date_published"] = soup.find("meta", itemprop="datePublished")['content']
    # get the duration of the video
    # result["duration"] = soup.find("span", {"class": "ytp-time-duration"}).text
    # get the video tags
    result["tags"] = ', '.join(
        [meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"})])

    # Additional video and channel information (with help from: https://stackoverflow.com/a/68262735)

    # data = re.search(r"var ytInitialData = ({.*?});", soup.prettify()).group(1)
    # data_json = json.loads(data)
    # videoPrimaryInfoRenderer =
    # data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
    # videoSecondaryInfoRenderer =
    # data_json['contents']['twoColumnWatchNextResults']
    # ['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
    #
    # number of likes
    # likes_label =
    # videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label']
    # "No likes" or "###,### likes"
    # likes_str = likes_label.split(' ')[0].replace(',','')
    # result["likes"] = '0' if likes_str == 'No' else likes_str
    # number of likes (old way) doesn't always work
    # text_yt_formatted_strings =
    # soup.find_all("yt-formatted-string", {"id": "text", "class": "ytd-toggle-button-renderer"})
    # result["likes"] = ''.join([ c for c in text_yt_formatted_strings[0].attrs.get("aria-label") if c.isdigit() ])
    # result["likes"] = 0 if result['likes'] == '' else int(result['likes'])
    # number of dislikes - YouTube does not publish this anymore...
    # result["dislikes"] = ''.join([ c for c in text_yt_formatted_strings[1].attrs.get("aria-label") if c.isdigit() ])
    # result["dislikes"] = '0' if result['dislikes'] == '' else result['dislikes']
    # result['dislikes'] = 'UNKNOWN'
    # channel details
    # channel_tag = soup.find("meta", itemprop="channelId")['content']
    # channel name
    result["channel_name"] = soup.find("span", itemprop="author").next.next['content']

    result['channel_url'] = soup.find("span", itemprop="author").find("link", itemprop="url").get('href')

    # channel URL
    # channel_url = soup.find("span", itemprop="author").next['href']
    # channel_url = f"https://www.youtube.com/{channel_tag}"
    # number of subscribers as str
    # channel_subscribers =
    # videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']
    # ['accessibility']['accessibilityData']['label']
    # channel details (old way)
    # channel_tag = soup.find("yt-formatted-string", {"class": "ytd-channel-name"}).find("a")
    # # channel name (old way)
    # channel_name = channel_tag.text
    # # channel URL (old way)
    # channel_url = f"https://www.youtube.com{channel_tag['href']}"
    # number of subscribers as str (old way)
    # channel_subscribers = soup.find("yt-formatted-string", {"id": "owner-sub-count"}).text.strip()
    # result['channel'] = {'name': channel_name, 'url': channel_url, 'subscribers': channel_subscribers}

    return result


def get_channel_info(url):
    soup = get_soup_of_html_session(url)
    result = dict()
    result["identifier"] = soup.find("meta", itemprop="identifier")['content']

    result["title"] = soup.find("meta", itemprop="name")['content']
    result["description"] = soup.find("meta", itemprop="description")['content']
    result["thumbnail_url"] = soup.find("link", itemprop="thumbnailUrl")['href']

    return result
