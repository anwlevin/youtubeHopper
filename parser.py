
import time

from bs4 import BeautifulSoup
from requests_html import HTMLSession

from selenium.webdriver import Keys, FirefoxOptions, Firefox
from selenium.webdriver.common.by import By


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
        for i in range(10):
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
    session = HTMLSession()

    response = session.get(url)

    soup = BeautifulSoup(response.html.html, "html.parser")
    return soup
