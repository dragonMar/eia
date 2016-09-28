#!/usr/bin/evn python
#coding:utf-8


import psycopg2


def conn_psql(sql):
    try:
        conn = psycopg2.connect(database="epbdc", user="deploy", password="Deploy123$", host="127.0.0.1", port="5432")
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print e
        print sql
    finally:
        conn.close()
