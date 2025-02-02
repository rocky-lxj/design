import csv
import os
import random
import requests
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import chardet

# 初始化 CSV 文件
def init_csv():
    if not os.path.exists('./lianjia_cityData.csv'):
        with open('./lianjia_cityData.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['quyulink', 'page'])

# 获取 HTML 页面内容
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

# 解析 HTML 页面，获取城市链接和名称
def parse_html1(html_text):
    text = etree.HTML(html_text)
    citylink = text.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div/div/a/@href')
    cityname = text.xpath('/html/body/div[3]/div/div[1]/dl[2]/dd/div/div/a/text()')
    city_dict = {key: value for key, value in zip(citylink, cityname)}
    # print(city_dict)
    base_url = 'https://xz.lianjia.com'
    for qu in citylink:
        parse_html2(base_url + qu, city_dict[qu])

# 初始化浏览器
def init_browser():
    service = Service('./chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')  # 开启无头模式
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('debuggerAddress', 'localhost:9222')  # 指定远程调试端口
    return webdriver.Chrome(service=service, options=options)

# 获取页面的总页数
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

# 解析 HTML 页面，获取区域链接和总页数
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
            with open('./lianjia_cityData.csv', 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([new_url, page])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()

# 主函数
def main():
    init_csv()
    url = 'https://xz.lianjia.com/ershoufang/'
    html_code = get_html(url)
    if html_code:
        parse_html1(html_code)

if __name__ == '__main__':
    main()