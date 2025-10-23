from calendar import c
import requests
from bs4 import BeautifulSoup

def crawl(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup


crawl('https://www.explainthis.io/zh-hans/chatgpt')