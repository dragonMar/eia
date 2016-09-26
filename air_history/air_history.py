#!/usr/bin/env python
#coding:utf-8


import time
import datetime
import Queue
import requests
import crawler
from mail import send_mail
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from conn_psql import conn_psql



max_request = 3
max_time = 3
message = []
create_time = datetime.datetime.now()
req_url = requests.session()
req_url.mount('http://', HTTPAdapter(max_retries=max_request))
req_url.mount('https://', HTTPAdapter(max_retries=max_request))


def crawl_html(url, fail_list):
    try:
        content = req_url.get(url)
        soup = bs(content.text, 'lxml')
        table = soup.find("table", {"id": "report1"})
        trs = table.findAll("tr", {"style": "height:30px;"})[2:]
        for tr in trs:
            tds = tr.findAll("td")
            sql = "INSERT INTO air_history(city, pubtime, api, level, pollution, status, create_time) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
            (\
            tds[1].text.replace('&nbsp;', '').strip(),\
            tds[2].text.replace('&nbsp;', '').strip(),\
            tds[3].text.replace('&nbsp;', '').strip(),\
            tds[4].text.replace('&nbsp;', '').strip(),\
            tds[5].text.replace('&nbsp;', '').strip(),\
            tds[6].text.replace('&nbsp;', '').strip(),\
            create_time \
            )
            conn_psql(sql, message)
            print sql
    except Exception, e:
        fail_list.append(url)
        print e

if __name__ == "__main__":
    message = {"start":'', "end": '', 'fail_url': ''}
    start = str(datetime.datetime.now())
    message["start"] = start
    url = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp"
    url_base = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp?city=&startdate=&enddate=&page={0}"
    url_queue = Queue.Queue()
    fail_list = []
    crawler.get_url(url, url_base=url_base, url_queue=url_queue)
    try:
        crawl_num = int(sys.argv[1])
    except:
        crawl_num = 50
    _st = time.time()
    wm = crawler.WorkManager(crawl_num)
    for i in range(url_queue.qsize()):
        wm.add_crawl(crawl_html, url_queue.get(), fail_list)
    wm.start()
    wm.wait_for_complete()
    end = str(datetime.datetime.now())
    message["end"] = end
    if len(fail_list) != 0:
        message["fail_url"] = fail_url
    print message
    send_mail("环保部城市空气质量日报历史", ','.join(message))
    print time.time() - _st
