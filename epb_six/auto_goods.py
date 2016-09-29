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
                da = {}
                da['batch'] = tds[1].text.replace("&nbsp;","").strip()
                da['approve_date'] = tds[2].text.replace("&nbsp;","").strip()
                da['import_unit'] = tds[3].text.replace("&nbsp;","").strip()
                da['manu_unit'] = tds[4].text.replace("&nbsp;","").strip()
                da['goods_code'] = tds[5].text.replace("&nbsp;","").strip()
                da['goods_name'] = tds[6].text.replace("&nbsp;","").strip()
                da['approve_amount'] = tds[7].text.replace("&nbsp;","").strip()
                da['approve_port'] = tds[8].text.replace("&nbsp;","").strip()
                da['create_time'] = create_time
                try:
                    da['approve_amount'] = int(da['approve_amount'])
                    if da['approve_amount']>=1000000000:
                        da['goods_code'] = da['goods_code'] + ',' + da['goods_name'] + ',' + str(da['approve_amount'])
                        da['approve_amount'] = 0
                        da['goods_name'] = ''
                        if da['approve_port']>=1000000000:
                            da['goods_code'] = da['goods_code'] + ',' + da['approve_port']
                            da['approve_port'] = ''
                except Exception, e:
                    if da['approve_amount'] == '':
                        da['approve_amount'] = 0
                    else:
                        if len(da['approve_amount'])>=3:
                            da['goods_code'] = da['goods_code'] + ',' + da['goods_name']
                            da['goods_name'] = da['approve_amount']
                            da['approve_amount'] = da['approve_port']
                            da['approve_port'] = ''
                        else:
                            tmp = da['approve_amount']
                            da['approve_amount'] = da['approve_port']
                            da['approve_port'] = tmp
                sql = "INSERT INTO auto_goods(batch, approve_date, import_unit, manu_unit, goods_code, goods_name, approve_amount, approve_port, create_time) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                    (da['batch'], da['approve_date'], da['import_unit'], da['manu_unit'], da['goods_code'], da['goods_name'], da['approve_amount'], da['approve_port'], da['create_time'])
                sqls.append(sql)
            conn_psql(sqls, message, data)
            print data, t
        else:
            content.raise_for_status()
    except Exception, e:
        fail_list.append(data)
        fail_list.append(traceback.format_exc())
        print data, e, t

if __name__ == "__main__":
    message = {"start":'', "end": '', 'fail_url': [], 'fail_insert': []}
    message["start"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url_count = "http://datacenter.mep.gov.cn/main/template-view.action?templateId_=4028801b29e888e70129e9b93c3e000b"
    url = "http://datacenter.mep.gov.cn/main/template-view.action"
    s = get_num(url_count)
    if not s:
        send_mail("限制类固体废物进口名单", "请求失败！")
    else:
        try:
            crawl_num = int(sys.argv[1])
        except:
            crawl_num = 10
        wm = crawler.WorkManager(crawl_num)
        for i in range(1,s+1):
            pag = {"templateId_": "4028801b29e888e70129e9b93c3e000b",\
                   "page.pageNo": i, "dataSource": "${dataSource}"}
            wm.add_crawl(crawl_html, url, message["fail_url"], message['fail_insert'], pag)
        wm.start()
        wm.wait_for_complete()
        message["end"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = "start at: %s <br> end at: %s <br> fail_url: %s <br> fail_insert: %s <br>" % (message['start'], message['end'], message['fail_url'], ';;'.join(message['fail_insert']))
        if len(message["fail_url"])==0 and len(message["fail_insert"])==0:
            data = data + "success!"
        send_mail("限制类固体废物进口名单", data)
