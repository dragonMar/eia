#!/user/bin/evn python
#coding:utf-8
#author:dragonMar


import datetime
import re
import requests
import threading
import Queue
from conn_psql import conn_psql
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup as bs
from mail import send_mail


create_time = datetime.datetime.now().strftime("%Y-%m-%d")
max_request = 3
max_time = 3
queue = Queue.Queue()
request_url = requests.session()
request_url.mount('http://', HTTPAdapter(max_retries=max_request))
request_url.mount('https://', HTTPAdapter(max_retries=max_request))
message = []


def get_data(url):
    try:
        page = request_url.get(url, timeout=max_time)
        soup = bs(page.content,"lxml")
        table = soup.find("table", {"style": "margin: 20px auto 0px auto"})
        trs = table.findAll("tr", {"name": "white"})
        for tr in trs:
            tds = tr.findAll("td")
            sql = "INSERT INTO person(nid, name, code, orgnization, province,\
                    credit, create_time) values ('%s', '%s', '%s', '%s', '%s',\
                    '%s', '%s')" % (\
                    tds[0].text.replace("&nbsp;","").strip(),\
                    tds[1].text.replace("&nbsp;","").strip(),\
                    tds[2].text.replace("&nbsp;","").strip(),\
                    tds[3].text.replace("&nbsp;","").strip(),\
                    tds[4].text.replace("&nbsp;","").strip(),\
                    tds[5].text.replace("&nbsp;","").strip(),\
                    create_time)
            conn_psql(sql, message)
       # print sql
    except Exception, e:
        print e



def get_page(url_count, url_base,queue):
    try:
        content = request_url.get(url_count, timeout=max_time)
        soup = bs(content.text, "lxml")
        div = soup.find("div", {"class": "yahoo"})
        a = div.findAll("a")
        page = a[1].get("href")
        page_nums = re.findall(r"\d+",page)
        page_count = int(page_nums[0])
        for page in range(1,page_count+1):
            url = url_base.format(page)
            queue.put(url)
    except Exception, e:
        message.append("获取页码错误！")


def main():
    url_count = "http://datacenter.mep.gov.cn/hpzzcx/query.do?talbeName=Hpsgry&new=true"
    url_base = "http://datacenter.mep.gov.cn/hpzzcx/query.do?talbeName=Hpsgry&pageNum={0}&new=true"
    get_page(url_count, url_base, queue)
    for i in range(queue.qsize()):
        url = queue.get()
        print url
        get_data(url)
    if len(message)!=0 :
        send_mail("抓取数据出错！", ','.join(message))
    else:
        print "success"


if __name__ == "__main__":
    main()
