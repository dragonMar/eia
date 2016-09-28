#!/usr/bin/env python
#coding:utf-8


import time
import datetime
import Queue
import requests
import crawler
import traceback
from mail import send_mail
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from conn_psql import conn_psql


max_timeout = 120
max_request = 3
create_time = datetime.datetime.now()
req_url = requests.session()
req_url.mount('http://', HTTPAdapter(max_retries=max_request))


def crawl_html(url, fail_list, message):
    try:
        sqls = []
        t = datetime.datetime.now()
        content = req_url.get(url, timeout=max_timeout)
        if content.status_code == 200:
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
                sqls.append(sql)
            conn_psql(sqls, message, url)
            print url, t
        else:
            content.raise_for_status()
    except Exception, e:
        fail_list.append(url)
        fail_list.append(traceback.format_exc())
        print url, e, t

if __name__ == "__main__":
    message = {"start":'', "end": '', 'fail_url': [], 'fail_insert': []}
    start = str(datetime.datetime.now())
    message["start"] = start
    url = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp"
    url_base = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp?city=&startdate=&enddate=&page={0}"
    url_queue = Queue.Queue()
    s = crawler.get_url(url, url_base=url_base, url_queue=url_queue)
    if not s:
        send_mail("环保部城市空气质量日报历史", "请求失败！")
    else:
        try:
            crawl_num = int(sys.argv[1])
        except:
            crawl_num = 10
        wm = crawler.WorkManager(crawl_num)
        for i in range(url_queue.qsize()):
            wm.add_crawl(crawl_html, url_queue.get(), message["fail_url"], message['fail_insert'])
        wm.start()
        wm.wait_for_complete()
        end = str(datetime.datetime.now())
        message["end"] = end
        data = "start at: %s <br> end at: %s <br> fail_url: %s <br> fail_insert: %s <br>" % (message['start'], message['end'], message['fail_url'], ';;'.join(message['fail_insert']))
        if len(message["fail_url"])==0 and len(message["fail_insert"])==0:
            data = data + "success!"
        send_mail("环保部城市空气质量日报历史", data)
