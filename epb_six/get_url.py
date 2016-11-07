#coding:utf-8

import re

def get_url():
    with open('1.log', 'r') as f:
        content = f.read()
        url1 = re.findall(r"http://.*?page=\d*", content)
        url1 = ','.join(url1)
        url = re.findall(r"http://.*?page=\d*", url1)
        '''
        url2 = re.findall(r"http://.*?503",content)
        url3 = re.findall(r"http://.*?HTTPCon", content)
        url4 = re.findall(r"http://.*?NoneType",content)
        _url =  url2 + url3 + url4
        url_ = ','.join(_url)
        url = re.findall(r"http://.*?page=\d*", url_)
        '''
        return  url

print len(get_url())
