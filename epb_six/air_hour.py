#!/usr/bin/env python
#coding:utf-8


import time
import datetime
import Queue
import unicodedata
import requests
import crawler
import traceback
from mail import send_mail
from bs4 import BeautifulSoup as bs
from requests.adapters import HTTPAdapter
from conn_psql import conn_psql, get_data


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
                aqi = tds[3].text.replace('&nbsp;', '').strip()   # 如果aqi非数字类型 将其赋值为0
                if aqi == '':
                    aqi = 0
                ptime = tds[2].text.replace('&nbsp;', '').strip()
                i = unicodedata.normalize("NFKD", ptime)
                pubtime = time.strptime(i, "%Y-%m-%d %H:%M")
                ptime = time.strftime("%Y-%m-%d %H:%M:%S", pubtime)
                sql = "INSERT INTO air_hour(city, pubtime, aqi, level, pollution) values ('%s', '%s', '%s', '%s', '%s')" % \
                      (\
                       tds[1].text.replace('&nbsp;', '').strip(),\
                       ptime,\
                       aqi,\
                       tds[4].text.replace('&nbsp;', '').strip(),\
                       tds[5].text.replace('&nbsp;', '').strip()\
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
    sql = "select pubtime from air_hour order by pubtime desc limit 1"
    t = get_data(sql, message['fail_insert'])
    if t is None:
        start_day = '2014-01-01 00:00'
    else:
        t = t[0] + datetime.timedelta(hours=1)
        start_day = t.strftime("%Y-%m-%d %H:%M")
    today = datetime.datetime.now()
    end_day = today.strftime("%Y-%m-%d")
    message["start"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = "http://datacenter.mep.gov.cn/report/air_daily/airDairyCityHour.jsp?city=&startdate=%s&enddate=%s 00:00" % (start_day, end_day)
    url_base = "http://datacenter.mep.gov.cn/report/air_daily/airDairyCityHour.jsp?city=&startdate=%s&enddate=%s 00:00&page={0}" % (start_day, end_day)
    url_queue = Queue.Queue()
    s = crawler.get_url(url, url_base=url_base, url_queue=url_queue)
    if not s:
        send_mail("环保部城市小时空气质量小时报", "请求失败！")
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
        message["end"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = "start at: %s <br> end at: %s <br> fail_url: %s <br> fail_insert: %s <br>" % (message['start'], message['end'], message['fail_url'], ';;'.join(message['fail_insert']))
        if len(message["fail_url"])==0 and len(message["fail_insert"])==0:
            data = data + "success!"
        send_mail("环保部城市小时空气质量小时报", data)
