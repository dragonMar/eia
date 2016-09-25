#!/usr/bin/env python
#coding:utf-8


import requests
import Queue
import datetime
import time
import threading
from bs4 import BeautifulSoup as bs
from conn_psql import conn_psql

req_url = requests.session()
message = []
create_time = datetime.datetime.now()

def get_url(url,  *args, **kwds):
    try:
        global req_url
        content = req_url.get(url)
        soup = bs(content.text, 'lxml')
        td = soup.find("td", {"colspan": "3"})
        font = td.findAll("font")
        page_num = int(font[1].text)
        print kwds
        for i in range(1, page_num+1):
            url_request = kwds["url_base"].format(i)
            kwds["url_queue"].put(url_request)
        return True
    except Exception, e:
        print e


class CrawlWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.work_queue = work_queue

    def run(self):
        while True:
            try:
                call, args, kwds = self.work_queue.get(False)
                result = call(*args, **kwds)
            except Queue.Empty:
                break

'''
class SavaWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.work_queue = work_queue

    def run(self):
        while True:
            try:
                call, args, kwds = self.work_queue.get(False)
                result = call(*args, **kwds)
            except Queue.Empty:
                break
'''

class WorkManager:
    def __init__(self, crawl_num):
        self.url_queue = Queue.Queue()
        self.crawl_works = []
        self._CrawlWork(crawl_num)

    def _CrawlWork(self, crawl_num):
        for i in range(crawl_num):
            crawl_work = CrawlWork(self.url_queue)
            self.crawl_works.append(crawl_work)

    def add_crawl(self, call, *args, **kwds):
        self.url_queue.put((call, args, kwds))

    def start(self):
        for w in self.crawl_works:
            w.start()

    def wait_for_complete(self):
        while len(self.crawl_works):
            crawl_worker = self.crawl_works.pop()
            crawl_worker.join()
            if crawl_worker.isAlive() and not self.url_queue.empty():
                self.crawl_works.append(crawl_worker)
        print "All jobs were complete."
 

def crawl_html(url):
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
        print e




if __name__ == "__main__":
    url = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp"
    url_base = "http://datacenter.mep.gov.cn/report/air_daily/air_dairy_aqi.jsp?city=&startdate=&enddate=&page={0}"
    url_queue = Queue.Queue()
    get_url(url, url_base=url_base,url_queue=url_queue)
    try:
        crawl_num = int(sys.argv[1])
    except:
        crawl_num = 50
    _st = time.time()
    wm = WorkManager(crawl_num)
    for i in range(url_queue.qsize()):
        wm.add_crawl(crawl_html, url_queue.get())
    wm.start()
    wm.wait_for_complete()
    print time.time() - _st
