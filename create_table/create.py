#!/usr/bin/evn python
#coding:utf-8


from conn_psql import conn_psql



person_sql = 'create table person(\
       id serial NOT NULL, nid integer,name character varying(20),\
       code character varying(20), orgnization character varying(50),\
       province character varying(20), credit character varying(2000),\
       create_date date)'

engineer_sql="CREATE TABLE engineer(\
        id serial NOT NULL,nid integer,name character varying(20),\
        organization character varying(50),code character varying(20),\
        type character varying(50),start_date date,stop_date date,\
        nvq_code character varying(20),credit character varying(2000),\
        create_time date)"


unit_sql = "CREATE TABLE unit\
        (id serial NOT NULL, nid integer  NOT NULL,province character varying(20),\
        city character varying(20), org_name character varying(50), \
        level character varying(1), cq_code character varying(20), \
        a_scope character varying(200), b_scope character varying(200), \
        table_scope character varying(10), valid_date date, \
        base_info character varying(500), cop character varying(20),\
        phone character varying(100), credit character varying(2000),\
        create_time date)"


air_history_sql = "create table air_history(\
        id serial NOT NULL, city character varying(20) NOT NULL,\
        pubtime timestamp, api integer, level character varying(20),\
        pollution character varying(20), status character varying(20),\
        create_time timestamp)"
air_daily_sql = "create table air_daily(\
        id serial NOT NULL, city character varying(20) NOT NULL,\
        pubtime timestamp, aqi integer, level character varying(20),\
        pollution character varying(20))"
air_hour_sql = "create table air_hour(\
        id serial NOT NULL, city character varying(20) NOT NULL,\
        pubtime timestamp, aqi integer, level character varying(20),\
        pollution character varying(20))"
epa_area_sql = "create table epa_area(\
        id serial NOT NULL, code character varying(20),\
        epa_name character varying(20), area character varying(50),\
        size float, objects character varying(50), kinds character varying(20),\
        level character varying(20), set_date timestamp, chargedby character varying(20),\
        create_time timestamp)"
limit_goods_sql =  "create table limit_goods(\
        id serial NOT NULL, year integer NOT NULL, batch integer,\
        approve_date timestamp, import_unit character varying(50),\
        manu_unit character varying(50), goods_code character varying(100), \
        goods_name character varying(50), approve_amount integer,\
        approve_port character varying(20),create_time timestamp)"
auto_goods_sql = "create table auto_goods(\
        id serial NOT NULL, batch integer NOT NULL, approve_date timestamp,\
        import_unit character varying(50), manu_unit character varying(50),\
        goods_code character varying(100), goods_name character varying(20),\
        approve_amount integer, approve_port character varying(30),\
        create_time timestamp)"


if __name__ =="__main__":
    #conn_psql(person_sql)
    #conn_psql(engineer_sql)
    #conn_psql(unit_sql)
    conn_psql(air_history_sql)
    conn_psql(air_daily_sql)
    conn_psql(air_hour_sql)
    conn_psql(epa_area_sql)
    conn_psql(limit_goods_sql)
    conn_psql(auto_goods_sql)

