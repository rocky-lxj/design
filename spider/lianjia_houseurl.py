import csv
import os
from lxml import etree
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
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

def init_csv():
    if not os.path.exists('./lianjia_houseurl.csv'):
        with open('./lianjia_houseurl.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

def parse_lianjia(base_url,page):
    for i in range(1,int(page)+1):
        url = base_url + "pg" + str(i)
        max_retries = 10  # 最大重试次数
        retries = 0
        while retries < max_retries:
            browser = init_browser()
            browser.get(url)
            html = browser.page_source
            text = etree.HTML(html)
            try:
                house_list = text.xpath('//*[@id="content"]/div[1]/ul/li[contains(@class, "clear") and contains(@class, "LOGCLICKDATA")]/a/@href')
                with open('./lianjia_houseurl.csv', 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for house_url in house_list:
                        writer.writerow([house_url])
                break
            except IndexError:  # 当 XPath 查找结果为空列表时，取索引 0 会引发 IndexError
                print("可能遇到人机验证，请手动完成验证后按 Enter 键继续...")
                x = input()  # 暂停程序，等待用户按 Enter 键
                if x == "1":
                    return
            except TimeoutException as e:
                print(f"Timeout error: {e}. Retrying ({retries + 1}/{max_retries})..." + url)
                # print(f"可能触发了人机认证，错误信息: {e}")
                print("请手动完成人机认证，完成后按回车键继续...")
                input()  # 等待用户输入回车
                retries += 1
                time.sleep(10)  # 等待 5 秒后重试
        if retries == max_retries:
            print("Failed after multiple retries." + url)
        
def lianjia():
    with open('./lianjia_addurl.csv') as csvfile:
        reader = csv.reader(csvfile)
        # next(reader)
        for row in reader:
            parse_lianjia(row[0],row[1])            

def clear():
    df = pd.read_csv('./lianjia_houseurl.csv')
    df.drop_duplicates(inplace=True)
    df.to_csv('./lianjia_houseurl.csv', index=False)
def main():
    init_csv()
    lianjia()
    clear()

if __name__ == '__main__':
    main()