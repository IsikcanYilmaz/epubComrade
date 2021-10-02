#!/usr/bin/env python3

import ebooklib
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:
    def __init__(self, url):
        pass

    def download_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        return requests.get(url, headers=headers).text
    
    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

if __name__ == '__main__':
    Crawler('https://www.marxist.com/marxism-direct-action-anarchism040500.htm')
