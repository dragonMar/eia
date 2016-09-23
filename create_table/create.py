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
        leve character varying(1), cq_code character varying(20), \
        a_scope character varying(200), b_scope character varying(200), \
        table_scope character varying(10), valid_date date, \
        base_info character varying(500), cop character varying(20),\
        phone character varying(100), credit character varying(2000),\
        create_time date)"


if __name__ =="__main__":
    conn_psql(person_sql)
    conn_psql(engineer_sql)
    conn_psql(unit_sql)

