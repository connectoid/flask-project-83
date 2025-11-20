import requests
from bs4 import BeautifulSoup

url = 'https://ya.ru'

def get_seo_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(url.text, 'lxml')
    seo_data = {}

    seo_data['h1'] = soup.find('h1')
    seo_data['title'] = soup.find('title')
    seo_data['meta'] = soup.find('meta')['content']
    return seo_data


seo_data = get_seo_data(url)
print(seo_data)