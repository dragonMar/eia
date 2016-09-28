#!/usr/bin/env python
#coding:utf-8


import re


def get_url():
    with open("fail.txt", "r") as f:
        content = f.read()
        com = re.compile("http://.*?\d*")
        lis = com.findall(content)
        print len(lis)

get_url()
