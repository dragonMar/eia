#!/usr/bin/evn python
#coding:utf-8
#author:dragonMar


import psycopg2
from mail import send_mail
import traceback



def conn_psql(sqls, message, url):
    try:
        conn = psycopg2.connect(database="epbdc", user="deploy", password="Deploy123$", host="127.0.0.1", port="5432")
        cur = conn.cursor()
        for sql in sqls:
            cur.execute(sql)
        conn.commit()
    except Exception, e:
        message.append(url)
        message.append(traceback.format_exc())
        print e
    finally:
        conn.close()

def get_data(sql, message):
    try:
        conn = psycopg2.connect(database='epbdc', user='deploy', password='Deploy123$', host='127.0.0.1', port='5432')
        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchone()
        return data
    except Exception, e:
        message.append(traceback.format_exc())
        print e
    finally:
        conn.close()
