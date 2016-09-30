#!/usr/bin/env python
#coding:utf-8
#author:dragonMar


import requests
import datetime
import threading
import Queue
from bs4 import BeautifulSoup as bs


def get_url(url, *args, **kwds):
    try:
        content = requests.session().get(url)
        soup = bs(content.text, 'lxml')
        td = soup.find("td", {"colspan": "3"})
        font = td.findAll("font")
        page_num = int(font[1].text)
        for i in range(1, page_num+1):
            url_request = kwds["url_base"].format(page_num-i+1)
            kwds["url_queue"].put(url_request)
        return True
    except Exception, e:
        print e
        return False


class CrawlWork(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.work_queue = work_queue

    def run(self):
        while True:
            try:
                call, args, kwds = self.work_queue.get(False)
                call(*args, **kwds)
            except Queue.Empty:
                break


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
