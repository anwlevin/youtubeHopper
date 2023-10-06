from requests_html import HTMLSession
from bs4 import BeautifulSoup as bs
import re
import json

session = HTMLSession()


def get_video_info(url):
    # download HTML code
    response = session.get(url)
    # execute Javascript
    # response.html.render(timeout=60)
    # create beautiful soup object to parse HTML
    #print(response.html.html)

    soup = bs(response.html.html, "html.parser")
    # open("index.html", "w").write(response.html.html)
    # initialize the result
    result = {}
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
    # videoPrimaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
    # videoSecondaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
    # number of likes
    # likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'] # "No likes" or "###,### likes"
    # likes_str = likes_label.split(' ')[0].replace(',','')
    # result["likes"] = '0' if likes_str == 'No' else likes_str
    # number of likes (old way) doesn't always work
    # text_yt_formatted_strings = soup.find_all("yt-formatted-string", {"id": "text", "class": "ytd-toggle-button-renderer"})
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
    # channel_subscribers = videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility']['accessibilityData']['label']
    # channel details (old way)
    # channel_tag = soup.find("yt-formatted-string", {"class": "ytd-channel-name"}).find("a")
    # # channel name (old way)
    # channel_name = channel_tag.text
    # # channel URL (old way)
    # channel_url = f"https://www.youtube.com{channel_tag['href']}"
    # number of subscribers as str (old way)
    # channel_subscribers = soup.find("yt-formatted-string", {"id": "owner-sub-count"}).text.strip()
    #result['channel'] = {'name': channel_name, 'url': channel_url, 'subscribers': channel_subscribers}

    return result



def get_channel_info(url):
    # download HTML code
    response = session.get(url)
    # execute Javascript
    #response.html.render(timeout=2)
    # create beautiful soup object to parse HTML
    #print(response.html.html)

    soup = bs(response.html.html, "html.parser")
    # open("index.html", "w").write(response.html.html)
    # initialize the result
    result = {}
    # video title
    result["identifier"] = soup.find("meta", itemprop="identifier")['content']

    result["title"] = soup.find("meta", itemprop="name")['content']
    result["description"] = soup.find("meta", itemprop="description")['content']
    result["thumbnail_url"] = soup.find("link", itemprop="thumbnailUrl")['href']
    #banner = soup.find('div', id='contentContainer').find('div', id='banner-editor')
    #print()
    #print(banner)
    #result["about"] = 'BANNER'

    #find(id='channel-name')['content']

    return result

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
    # videoPrimaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']
    # videoSecondaryInfoRenderer = data_json['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']
    # number of likes
    # likes_label = videoPrimaryInfoRenderer['videoActions']['menuRenderer']['topLevelButtons'][0]['toggleButtonRenderer']['defaultText']['accessibility']['accessibilityData']['label'] # "No likes" or "###,### likes"
    # likes_str = likes_label.split(' ')[0].replace(',','')
    # result["likes"] = '0' if likes_str == 'No' else likes_str
    # number of likes (old way) doesn't always work
    # text_yt_formatted_strings = soup.find_all("yt-formatted-string", {"id": "text", "class": "ytd-toggle-button-renderer"})
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
    # channel_subscribers = videoSecondaryInfoRenderer['owner']['videoOwnerRenderer']['subscriberCountText']['accessibility']['accessibilityData']['label']
    # channel details (old way)
    # channel_tag = soup.find("yt-formatted-string", {"class": "ytd-channel-name"}).find("a")
    # # channel name (old way)
    # channel_name = channel_tag.text
    # # channel URL (old way)
    # channel_url = f"https://www.youtube.com{channel_tag['href']}"
    # number of subscribers as str (old way)
    # channel_subscribers = soup.find("yt-formatted-string", {"id": "owner-sub-count"}).text.strip()
    #result['channel'] = {'name': channel_name, 'url': channel_url, 'subscribers': channel_subscribers}

    return result
