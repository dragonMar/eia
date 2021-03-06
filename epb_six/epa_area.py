#!/usr/bin/env python
#coding:utf-8
#author:dragonMar


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


def get_num(url):
    try:
        content = req_url.get(url, timeout=max_timeout)
        soup = bs(content.text, 'lxml')
        td = soup.find("td", {"width": "30%"})
        font = td.findAll("font")
        num = int(font[1].text)
        return num
    except Exception, e:
        print e
        return False

def crawl_html(url, fail_list, message, data):
    try:
        sqls = []
        t = datetime.datetime.now()
        content = req_url.post(url, data=data, timeout=max_timeout)
        if content.status_code == 200:
            soup = bs(content.text, 'lxml')
            trs = soup.findAll("tr", {"name": "white"})
            for tr in trs:
                tds = tr.findAll("td")
                sql = "INSERT INTO epa_area(code, epa_name, area, size, objects, kinds, level, set_date, chargedby, create_time) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                    (\
                     tds[1].text.replace('&nbsp;', '').strip(),\
                     tds[2].text.replace('&nbsp;', '').strip(),\
                     tds[3].text.replace('&nbsp;', '').strip(),\
                     tds[4].text.replace('&nbsp;', '').strip(),\
                     tds[5].text.replace('&nbsp;', '').strip(),\
                     tds[6].text.replace('&nbsp;', '').strip(),\
                     tds[7].text.replace('&nbsp;', '').strip(),\
                     tds[8].text.replace('&nbsp;', '').strip(),\
                     tds[9].text.replace('&nbsp;', '').strip(),\
                     create_time \
                    )
                sqls.append(sql)
            conn_psql(sqls, message, data)
            print data, t
        else:
            content.raise_fot_status()
    except Exception, e:
        fail_list.append(data)
        fail_list.append(traceback.format_exc())
        print data, e, t

if __name__ == "__main__":
    message = {"start":'', "end": '', 'fail_url': [], 'fail_insert': []}
    message["start"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_count = "http://datacenter.mep.gov.cn/main/template-view.action?templateId_=8ae5e48d2670761801267088e590000b&dataSource="
    url = "http://datacenter.mep.gov.cn/main/template-view.action"
    s = get_num(url_count)

    if not s:
        send_mail("全国自然保护区名录（截至2011年底）", "请求失败！")
    else:
        try:
            crawl_num = int(sys.argv[1])
        except:
            crawl_num = 50
        wm = crawler.WorkManager(crawl_num)
        for i in range(1, s+1):
            pag = {"templateId_": "8ae5e48d2670761801267088e590000b",\
                   "page.pageNo": i}
            wm.add_crawl(crawl_html, url, message["fail_url"], message['fail_insert'], pag)
        wm.start()
        wm.wait_for_complete()
        message["end"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = "start at: %s <br> end at: %s <br> fail_url: %s <br> fail_insert: %s <br>" % (message['start'], message['end'], message['fail_url'], ';;'.join(message['fail_insert']))
        if len(message["fail_url"])==0 and len(message["fail_insert"])==0:
            data = data + "success!"
        send_mail("全国自然保护区名录（截至2011年底）", data)
