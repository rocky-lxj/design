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

def init_csv():
    if not os.path.exists('./houseinfo.csv'):
        with open('./houseinfo.csv', 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['小区名','面积', '照片','性质','区域','具体区域','室','厅','装修','网址','挂牌时间','总价','单价','朝向','房本年限'])


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

def parse_lianjia(base_url,page):
    for i in range(1,int(page)):
        url = base_url + "pg" + str(i)
        # print(url)
        browser = init_browser()
        browser.get(url)
        html = browser.page_source
        text = etree.HTML(html)
        # 修正引号和类名选择器
        house_list = text.xpath('//*[@id="content"]/div[1]/ul/li[contains(@class, "clear") and contains(@class, "LOGCLICKDATA")]/a/@href')
        print(house_list)
        for url in house_list:
            # time.sleep(5)
            parse_lianjia_page(url)
        # browser.quit()

def parse_lianjia_page(url):
    max_retries = 10  # 最大重试次数
    retries = 0
    while retries < max_retries:
        browser = init_browser()
        browser.get(url)
        html = browser.page_source
        text = etree.HTML(html)
        try:
            name = text.xpath('/html/body/div[5]/div[2]/div[4]/div[1]/a[1]/text()')[0]
            mianji = text.xpath('//*[@id="introduction"]/div/div/div[2]/div[2]/ul/li[5]/span[2]/text()')[0]
            zhaopian = text.xpath('//*[@id="topImg"]/div[1]/img/@src')[0]
            xingzhi = text.xpath('//*[@id="introduction"]/div/div/div[2]/div[2]/ul/li[2]/span[2]/text()')[0]
            quyu = text.xpath('/html/body/div[5]/div[2]/div[4]/div[2]/span[2]/a[1]/text()')[0]
            jutiquyu = text.xpath('/html/body/div[5]/div[2]/div[4]/div[2]/span[2]/a[2]/text()')[0]
            shiting = text.xpath('/html/body/div[5]/div[2]/div[3]/div[1]/div[1]/text()')[0]
            shi = shiting[0]
            ting = shiting[2]
            zhuangxiu = text.xpath('/html/body/div[7]/div[1]/div[1]/div/div/div[1]/div[2]/ul/li[9]/span/following-sibling::text() ')[0]
            # print(url + zhuangxiu)
            tim = text.xpath('//*[@id="introduction"]/div/div/div[2]/div[2]/ul/li[1]/span[2]/text()')[0]
            zongjia = text.xpath('/html/body/div[5]/div[2]/div[2]/div/span[1]/text()')[0]
            danjia = text.xpath('/html/body/div[5]/div[2]/div[2]/div/div[1]/div[1]/span/text()')[0] + '元/㎡'
            chaoxiang = text.xpath('/html/body/div[5]/div[2]/div[3]/div[2]/div[1]/text()')[0]
            wangzhi = url
            nianxian = text.xpath('//*[@id="introduction"]/div/div/div[2]/div[2]/ul/li[5]/span[2]/text()')[0]

            with open('./houseinfo.csv', 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [name, mianji, zhaopian, xingzhi, quyu, jutiquyu, shi, ting, zhuangxiu, wangzhi, tim, zongjia,
                     danjia, chaoxiang, nianxian])
            # browser.quit()
            break
        except IndexError:  # 当 XPath 查找结果为空列表时，取索引 0 会引发 IndexError
            print("可能遇到人机验证，请手动完成验证后按 Enter 键继续...")
            x=input()  # 暂停程序，等待用户按 Enter 键
            if x=="1":
                return
        except TimeoutException as e:
            print(f"Timeout error: {e}. Retrying ({retries + 1}/{max_retries})..."+url)
            # print(f"可能触发了人机认证，错误信息: {e}")
            print("请手动完成人机认证，完成后按回车键继续...")
            input()  # 等待用户输入回车
            retries += 1
            time.sleep(10)  # 等待 5 秒后重试
    if retries == max_retries:
        print("Failed after multiple retries."+url)



def parse_anjuke_page(url,zhaopian):
    if "xinfang" in url:
        return
    max_retries = 10  # 最大重试次数
    retries = 0
    while retries < max_retries:
        try:
            browser = init_browser()
            browser.get(url)
            html = browser.page_source
            text = etree.HTML(html)
            name = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[4]/div[2]/div[1]/a[1]/text()')[0]
            mianji = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[3]/div[2]/div[1]/i/text()')[0]
            # zhaopian = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[1]/section/div[1]/div/div/div/div[1]/div[1]/img/@src')[0]

            xingzhi = text.xpath('//*[@id="houseInfo"]/table/tbody/tr[1]/td[2]/span[2]/text()')[0]
            quyu = \
            text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[4]/div[2]/div[2]/span[2]/a[1]/text()')[
                0] + "区"
            jutiquyu = \
            text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[4]/div[2]/div[2]/span[2]/a[2]/text()')[
                0]
            shi = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/i[1]/text()')[0]
            ting = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[3]/div[1]/div[1]/i[2]/text()')[0]
            zhuangxiu = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[3]/div[2]/div[2]/text()')[0]
            tim = text.xpath('//*[@id="houseInfo"]/table/tbody/tr[7]/td[2]/span[2]/text()')[0]
            zongjia = \
            text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div[1]/span[1]/text()')[0]
            danjia = \
            text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/text()')[0]
            chaoxiang = text.xpath('//*[@id="__layout"]/div/div[3]/div[2]/div[2]/div[1]/div[3]/div[3]/div[1]/i/text()')[
                0]
            wangzhi = url
            nianxian = text.xpath('//*[@id="houseInfo"]/table/tbody/tr[2]/td[3]/span[2]/text()')[0]
            with open('./houseinfo.csv', 'a', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    [name, mianji, zhaopian, xingzhi, quyu, jutiquyu, shi, ting, zhuangxiu, wangzhi, time, zongjia,
                     danjia, chaoxiang, nianxian])
            # browser.quit()
            break  # 请求成功，退出重试循环
        #except IndexError as e:  # 当 XPath 查找结果为空列表时，取索引 0 会引发 IndexError
        #    print("可能遇到人机验证，请手动完成验证后按 Enter 键继续..."+url)
        #    print(e)
        #    x = input()  # 暂停程序，等待用户按 Enter 键
        #    if x == "1":
        #        return

        except TimeoutException as e:
            print(f"Timeout error: {e}. Retrying ({retries + 1}/{max_retries})..."+url)
            print("请手动完成人机认证，完成后按回车键继续..."+url)
            input()  # 等待用户输入回车
            retries += 1
            time.sleep(10)  # 等待 5 秒后重试
    if retries == max_retries:
        print("Failed after multiple retries." + url)


def lianjia():
    with open('./lianjia_cityData.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            parse_lianjia(row[0],row[1])

def parse_anjuke(base_url,page):
    for i in range(1,int(page)):
        url = base_url + "p" + str(i)
        # print(url)
        browser = init_browser()
        browser.get(url)
        html = browser.page_source
        text = etree.HTML(html)
        house_list = text.xpath('//*[@id="esfMain"]/section/section[3]/section[1]/section[2]/div/a/@href')
        # // *[ @ id = "esfMain"] / section / section[3] / section[1] / section[2]
        house_zhaopian = text.xpath('//*[@id="esfMain"]/section/section[3]/section[1]/section[2]/div/a/div/img/@src')
        house_zhaopian = house_zhaopian[:len(house_list)]
        # print(str(len(house_zhaopian))+" "+str(len(house_list)))
        # print(len(house_list))
        for i in range(0,len(house_list)):
            # time.sleep(5)
            parse_anjuke_page(house_list[i],house_zhaopian[i])
        # browser.quit()
def anjuke():
    with open('./anjuke_cityData.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            parse_anjuke(row[0],row[1])
def main():
    init_csv()
    lianjia()
    # anjuke()

if __name__ == '__main__':
    main()

#chrome.exe --remote-debugging-port=9222