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
    if not os.path.exists('./anjuke_cityData.csv'):
        with open('./anjuke_cityData.csv', 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['quyulink', 'page'])

# 解析 HTML 页面，获取城市链接和名称
def parse_html1(html_text):
    text = etree.HTML(html_text)
    citylink = text.xpath('//*[@id="ajk-home"]/div[1]/div[6]/div[3]/div/div[2]/div[2]/div/div/div[1]/div[1]/a/@href')
    cityname = text.xpath('//*[@id="ajk-home"]/div[1]/div[6]/div[3]/div/div[2]/div[2]/div/div/div[1]/div[1]/a/text()')
    city_dict = {key: value for key, value in zip(citylink, cityname)}
    # print(city_dict)
    # base_url = 'https://xz.lianjia.com'
    for qu in citylink:
        parse_html2(qu, city_dict[qu])

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
        page_numbers = text.xpath('//*[@id="esfMain"]/section/section[3]/section[1]/section[4]/div/ul/li[@class="page-item last"]/a/text()')
        # page_numbers = list(map(int, page_numbers))
        # print(page_numbers)
        if len(page_numbers) == 0:
            return 1;
        else :
            return int(page_numbers[0])
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
        citylink = text.xpath('//*[@id="esfMain"]/section/section[2]/div/section/div[1]/section/ul[2]/li/a/@href')
        print(name)
        citylink = citylink[1:]
        for local in citylink:
            new_url =  local
            print(new_url)
            page = get_page(new_url)
            print(page)
            with open('./anjuke_cityData.csv', 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([new_url, page])
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()
def clear():
    df = pd.read_csv('./lianjia_cityData.csv')
    df = df.drop_duplicates()
    df.to_csv('./lianjia_cityData.csv', index=False)
    
def main():
    init_csv()
    url = 'https://xuzhou.anjuke.com/'
    browser = init_browser()
    try:
        browser.get(url)
        html_text = browser.page_source
        parse_html1(html_text)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        browser.quit()
    clear();

if __name__ == '__main__':
    main()