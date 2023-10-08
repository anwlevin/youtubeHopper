
import re
import json


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

    js_data = json.loads(re_search_result.group(1))

    return js_data




