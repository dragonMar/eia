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
out_queue = Queue.Queue()
fail_queue = Queue.Queue()
request_url = requests.session()
request_url.mount('http://', HTTPAdapter(max_retries=max_request))
request_url.mount('https://', HTTPAdapter(max_retries=max_request))
message = []

class thread_url(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue
        self.request_url = request_url

    def run(self):
        while not self.queue.empty():
            try:
                url = self.queue.get()
                print url
                content = self.request_url.get(url, timeout=max_time)
                self.out_queue.put(content)
            except Exception, e:
                print e
                message.append("获取页面信息错误！")


class thread_date(threading.Thread):
    def __init__(self, out_queue):
        threading.Thread.__init__(self)
        self.out_queue = out_queue

    def run(self):
        while not self.out_queue.empty():
            content = self.out_queue.get()
            #print content
            soup = bs(content.text,"lxml")
            table = soup.find("table", {"style": "margin: 20px auto 0px auto"})
            trs = table.findAll("tr", {"name": "white"})
            for tr in trs:
                tds = tr.findAll("td")
                sql = "INSERT INTO engineer( nid, name, organization, code, type, start_date,\
                        stop_date, nvq_code, credit, create_time) VALUES ('%s', '%s', '%s', '%s', '%s',\
                        '%s', '%s', '%s', '%s', '%s')" \
                             % (
                                tds[0].text.replace("&nbsp;", "").strip(),\
                                tds[1].text.replace("&nbsp;", "").strip(),\
                                tds[2].text.replace("&nbsp;", "").strip(),\
                                tds[3].text.replace("&nbsp;", "").strip(),\
                                tds[4].text.replace("&nbsp;", "").strip(),\
                                tds[5].text.replace("&nbsp;", "").strip(),\
                                tds[6].text.replace("&nbsp;", "").strip(),\
                                tds[7].text.replace("&nbsp;", "").strip(),\
                                tds[8].text.replace("&nbsp;", "").strip(),\
                                create_time
                             )
                conn_psql(sql, message)
            #print sql
            self.out_queue.task_done()



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
        print e
        message.append("获取页码错误！")




if __name__ == "__main__":
    url_count = "http://datacenter.mep.gov.cn/hpzzcx/query.do?talbeName=Hpgcs&new=true"
    url_base = "http://datacenter.mep.gov.cn/hpzzcx/query.do?talbeName=Hpgcs&pageNum={0}"
    get_page(url_count, url_base, queue)
    for i in range(10):
        t = thread_url(queue, out_queue)
        t.start()
        t.join()
    for i in range(10):
        t = thread_date(out_queue)
        t.start()
        t.join()
    if len(message)!=0 :
        send_mail("抓取数据出错！", ','.join(message))
    else:
        print "success"

