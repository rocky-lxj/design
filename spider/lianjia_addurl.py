import csv
import os
import random
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import chardet
import pandas as pd

def init_browser():
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')  # 开启无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--timeout=300')
    options.add_experimental_option('debuggerAddress', 'localhost:9222')  # 指定远程调试端口
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(6000000)
    driver.set_script_timeout(60000000)
    return driver
def get_page(url):
    browser = init_browser()
    try:
        browser.get(url)
        html_text = browser.page_source
        text = etree.HTML(html_text)
        page_numbers = text.xpath('//*[@id="content"]/div[1]/div[7]/div[2]/div/a/@data-page')
        page_numbers = list(map(int, page_numbers))
        if len(page_numbers) >= 2 and page_numbers[-2] > page_numbers[-1]:
            return page_numbers[-2]
        elif len(page_numbers) == 0:
            return 1
        else:
            return max(page_numbers)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()
def init_csv():
    if not os.path.exists('lianjia_addurl.csv'):
        with open('lianjia_addurl.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['quyulink', 'page'])

def get_html(url):
    user_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0'
    ]
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "User-Agent": random.choice(user_agent)
    }
    session = requests.Session()
    response = session.get(url, headers=headers)
    response.encoding = chardet.detect(response.content)['encoding']
    if response.status_code == 200:
        return response.text
    else:
        return None
def parse_html1(html_text):
    text = etree.HTML(html_text)
    citylink = text.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div/div/a/@href')
    cityname = text.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div/div/a/text()')
    city_dict = {key: value for key, value in zip(citylink, cityname)}
    # print(city_dict)
    base_url = 'https://xz.lianjia.com'
    for qu in citylink:
        parse_html2(base_url + qu, city_dict[qu])
def clear():
    df = pd.read_csv('./lianjia_addurl.csv')
    df = df.drop_duplicates()
    df.to_csv('./lianjia_addurl.csv', index=False)
def parse_html2(url, name):
    browser = init_browser()
    try:
        browser.get(url)
        html_text = browser.page_source
        text = etree.HTML(html_text)
        citylink = text.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div/div[2]/a/@href')
        base_url = 'https://xz.lianjia.com'
        for local in citylink:
            new_url = base_url + local
            print(new_url)
            page = get_page(new_url)
            print(page)
            with open('lianjia_addurl.csv', 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([new_url, int(page)])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()
def main():
    init_csv()
    url = 'https://xz.lianjia.com/ershoufang/'
    html_code = get_html(url)
    if html_code:
        parse_html1(html_code)
    clear()

if __name__ == '__main__':
    main()