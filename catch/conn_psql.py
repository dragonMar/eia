#!/usr/bin/evn python
#coding:utf-8


import psycopg2
from mail import send_mail



def conn_psql(sql, message):
    try:
        conn = psycopg2.connect(database="epbdc", user="deploy", password="Deploy123$", host="127.0.0.1", port="5432")
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print e
        message.append("插入数据错误！")
    finally:
        conn.close()
