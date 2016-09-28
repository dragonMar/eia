#!/usr/bin/env python
#coding:utf-8


import re

f = open("fail.txt", 'r')
url = f.read()
r = re.compile("http://.*?page=\d*")
lis = r.findall(url)
print lis
print len(lis)
f.close()
