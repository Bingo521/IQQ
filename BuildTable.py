import sqlite3

import sys
from POTOCOL import *
import pickle
conn=sqlite3.connect('IQQ.db')
c=conn.cursor()
def fun():
    print(__file__,sys._getframe().f_code.co_name,sys._getframe().f_lineno)
c.execute("drop table user")
c.execute('''create table user(count integer PRIMARY KEY ,password text,username text)''')
c.execute("drop table friend")
c.execute("create table friend(count1 integer,count2 integer,PRIMARY KEY (count1,count2))")
c.execute("drop table chat")
c.execute("create table chat(id integer PRIMARY KEY ,count1 integer,count2 integer,msg blob,idate TIMESTAMP NOT NULL DEFAULT current_timestamp)")
c.execute("drop table Mess")
c.execute("create table Mess(id integer,res integer,des integer,type integer,pt BLOB,idate TIMESTAMP NOT NULL DEFAULT current_timestamp)")
conn.commit()
conn.close()

