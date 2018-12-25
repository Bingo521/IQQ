import sqlite3
from POTOCOL import POTOCOL
import threading
import os
import time
class MySQL(object):
    lock=threading.Lock()
    @staticmethod
    def execute(sql,args=0):
        MySQL.lock.acquire()
        db = sqlite3.connect(POTOCOL.DBNAME)
        c=db.cursor()
        if args==0:
            c.execute(sql)
        else:
           c.execute(sql,args)
        li=c.fetchall()
        db.commit()
        db.close()

        MySQL.lock.release()
        return li
class Log(object):
    LogPath=os.path.split(os.path.realpath(__file__))[0]
    lock=threading.Lock()
    @staticmethod
    def Print(tip,str,type=POTOCOL.LOGDEBUG):
        if type==POTOCOL.LOGDEBUG and POTOCOL.DEBUG==0:
            return
        t1=time.strftime('%Y-%m-%d', time.localtime(time.time()))
        t=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        file=POTOCOL.LOGNAME+t1+".log"
        filepath=Log.LogPath+"/"+file
        log = "[{0}][{1}][{2}][{3}]\n".format(type,tip,t, str)
        Log.lock.acquire()
        if not os.path.exists(filepath):
            fd1=open(filepath,"w",encoding="utf-8")
            fd1.close()
        fd=open(filepath,"a",encoding="utf-8")
        fd.write(log)
        fd.close()
        Log.lock.release()

