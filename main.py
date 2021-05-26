import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse
import re

START_URL = 'https://ys.mihoyo.com/main/character/mondstadt?char=0'


class HtmlReader:
    def __init__(self) -> None:
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/68.0.3440.106 Safari/537.36',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh,en-US;q=0.9,en;q=0.8',
        }
        self.timeout = 10

    def get_html(self, url: str) -> str:
        try:
            r = requests.get(url, headers=self.headers, timeout=self.timeout)
            return r.text
        except ConnectionError as e:
            print(f'Cannot reach {url}. {e}')
            return None

    def download(self, url: str, path: Path) -> None:
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        if r.status_code == 200:
            with path.open('wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            print(f'Cannot download {url}')


class DynamicHtmlReader:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('log-level=3')
        self.url = ''
        self.driver = webdriver.Chrome(options=options)

    def get_html(self, url: str) -> str:
        self.driver.get(url)
        self.url = self.driver.current_url
        return self.driver.page_source

    def close(self):
        self.driver.close()


def main():
    d_reader = DynamicHtmlReader()
    reader = HtmlReader()
    html = d_reader.get_html(START_URL)
    soup = BeautifulSoup(html, 'lxml')
    hostname = urlparse(START_URL).netloc

    # 输出文件夹
    output_dir = Path('output')
    if not output_dir.exists():
        output_dir.mkdir()

    def get_chars_in_city(url: str, city: str, html=None):
        if not html:
            _reader = DynamicHtmlReader()
            html = _reader.get_html('https://' + url)
            _reader.close()
        soup = BeautifulSoup(html, 'lxml')
        output = output_dir / city
        if not output.exists():
            output.mkdir()
        for img in soup('img', class_='character__person'):
            src = img['src']
            filename = re.search(r'\d+\.png', src).group()
            reader.download(src, output_dir / city / filename)

    # 获取所有城市
    for li in soup('li', class_='character__city'):
        a = li.a
        if not a:
            continue
        city_name = a.string.strip()
        print(a.string, a['href'])
        city_url = hostname + a['href']
        if city_name == '蒙德城':
            get_chars_in_city(city_url, city_name, html)
        else:
            get_chars_in_city(city_url, city_name)

    d_reader.close()


if __name__ == '__main__':
    main()
