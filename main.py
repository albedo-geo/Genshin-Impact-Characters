from os import read
from socket import INADDR_MAX_LOCAL_GROUP
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import re

url = 'https://ys.mihoyo.com/main/character/mondstadt?char=0'


class DynamicHtmlReader:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(options=options)

    def get_html(self, url: str) -> str:
        self.driver.get(url)
        return self.driver.page_source

    def close(self):
        self.driver.close()


def get_html(url: str) -> str:
    try:
        r = requests.get(url)
        return r.text
    except ConnectionError as e:
        print(f'Cannot reach {url}. {e}')


def download(url: str, path):
    pass


reader = DynamicHtmlReader()
html = reader.get_html(url)
soup = BeautifulSoup(html, 'lxml')
# for img in soup('img', class_='character__person'):
#     print(img['src'])
for li in soup('li', class_='character__city'):
    a = li.a
    if not a:
        continue
    print(a.string, a['href'])
reader.close()