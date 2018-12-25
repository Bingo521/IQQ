import pickle
import socket
import threading
import sqlite3
import time
import sys
from POTOCOL import *
from util import *

class Server(object):
    countMap = dict()
    COUNTBASE=123460
    WATERID =0
    CHATID=0
    def __init__(self,conn,addr):

        self.conn = conn
        self.fd=self.conn.makefile(mode="rwb")
        self.addr=addr
        self.count=None
        self.date=None
        self.funcMap = {
            POTOCOL.UADDF: self.AddFriend,
            POTOCOL.ULOGIN: self.Login,
            POTOCOL.UOFFLINE: self.Offline,
            POTOCOL.USENDWORD: self.SendWord,
            POTOCOL.UREGITSER:self.Register,
            POTOCOL.UAGREE:self.Agree,
            POTOCOL.UREFUSE:self.Refuse,
            POTOCOL.UDELETEINFO:self.DeleteWater,
            POTOCOL.UMESS:self.TalkIntoDB,
            POTOCOL.UDELETEF:self.DeleteFriend,
            POTOCOL.USENDFILE:self.RecvFile,
            POTOCOL.UGETFILE:self.SendFile
        }


        self.messdate=None
        self.run()
    def run(self):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__,sys._getframe().f_code.co_name,sys._getframe().f_lineno,self.count),"链接成功！IP={0},PORT={1}".format(self.addr[0],self.addr[1]),POTOCOL.LOGINFO)
        data=None
        while True:
            try:
                data=pickle.load(self.fd)
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),data.pno)
                self.funcMap[data.pno](data)
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"run go on")
            except Exception as e:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),e,POTOCOL.LOGERROR)
                if self.count!=None:
                    self.changeStaus(0)
                    lock.acquire()
                    conn=Server.countMap.get(self.count)
                    if conn!=None:
                        Server.countMap.pop(self.count)
                    lock.release()
                if self.count!=None:
                    Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}离线!!!...".format(self.count),POTOCOL.LOGINFO)
                elif data!=None and data.pno==POTOCOL.USENDFILE:
                    Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"接收文件完成",POTOCOL.LOGINFO)
                else:
                    Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"对方建立链接后主动断开",POTOCOL.LOGINFO)
                break
    def Login(self,data):
        count=data.data.get(POTOCOL.COUNT)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(count))
        password=data.data.get(POTOCOL.PASSWORD)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}正在尝试链接...".format(count),POTOCOL.LOGINFO)
        if count==None or password==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"error potocol!",POTOCOL.LOGERROR)

        lock.acquire()
        conn=self.countMap.get(count)
        lock.release()
        if conn!=None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}已存在！".format(count))
            pt=MyPotocol(POTOCOL.SMESSBOX,"你已经登陆过一次！")
            pdata=pickle.dumps(pt)
            self.conn.sendall(pdata)
            return

        li=MySQL.execute("select * from user where count={0} and password='{1}'".format(count,password))


        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"关闭数据库")
        if len(li)>0:
            pt = MyPotocol(POTOCOL.SSUCCESS)
            pdata=pickle.dumps(pt)
            self.conn.sendall(pdata)
            lock.acquire()
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"已存入%d"%count,POTOCOL.LOGINFO)
            Server.countMap[count]=self.conn
            lock.release()
            self.count=count
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}登陆成功！".format(count),POTOCOL.LOGINFO)
            self.user=User(count=li[0][0],isOnLine=1,username=li[0][2])
            self.InitChat()
            self.changeStaus(1)
        else:
            pt=MyPotocol(POTOCOL.SMESSBOX,"用户名密码错误！")
            pdata=pickle.dumps(pt)
            self.conn.sendall(pdata)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}登陆失败！".format(count),POTOCOL.LOGINFO)
    def RecvFile(self,pt):
        print("开始接收文件")
        reldata = pt.data
        res = reldata[POTOCOL.RES]
        des = reldata[POTOCOL.DES]
        file=reldata[POTOCOL.FILE]
        li = MySQL.execute("select * from friend where count1={0} and count2={1} or count1={1} and count2={0}".format(res, des))
        if len(li) == 0:
            pt = MyPotocol(POTOCOL.SMESSBOX, "发送失败！对方不是您的好友！")
            pdata = pickle.dumps(pt)
            self.conn.sendall(pdata)
            return
        id=self.Transpond(pt,POTOCOL.MFILE)
        print(id,file.filename,file.file)
        lenth=file.file
        file = open("{1}/{0}.file".format(id,POTOCOL.PATHFILE), "wb")

        try:

            while True:
                data=pickle.load(self.fd)
                file.write(data)
                lenth-=len(data)
            pass

        except Exception as e:
            print(e)
            if lenth!=0:
                MySQL.execute("delete from Mess where id={0}".format(id))
            pass
        finally:
            file.close()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count), "接收文件完成")
        print("OK")
    def MessageBox(self,data):
        pt=MyPotocol(POTOCOL.SMESSBOX,data)
        pdata=pickle.dumps(pt)
        self.conn.sendall(pdata)
    def DeleteWater(self,pt):

        id=pt.data.get(POTOCOL.INFOID)
        if id==None:
            self.MessageBox("删除id错误")

        MySQL.execute("delete from Mess where id={0}".format(id))

        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"删除第{0}项完成！".format(id),POTOCOL.LOGINFO)
    def InitChat(self):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"InitChat 开始")

        pt=MyPotocol(POTOCOL.SINITSELF,{POTOCOL.USER:self.user})
        pdata=pickle.dumps(pt)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发送初始化用户数据")
        self.conn.sendall(pdata)
        li=MySQL.execute("select * from friend where count1={0} or count2={1}".format(self.count,self.count))

        fl=[]
        fcl=[]
        #开始查询好友ID
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始查询好友ID")
        for item in li:
            if item[0]==self.count:
                fcl.append(item[1])
            else:
                fcl.append(item[0])
        #开始查询好友信息
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始查询好友信息")
        for item in fcl:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),item)
            fname=MySQL.execute("select username from user where count={0}".format(item))
            #fname=c.fetchall()
            lenf=len(fname)
            if lenf<=0:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"InitChat：好友列表中存在不存在的好友！",POTOCOL.LOGINFO)
                continue
            elif lenf>1:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"InitChat：主键错误！存在相同账号！",POTOCOL.LOGINFO)
                continue
            else:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"好友{0}".format(item))
                onLine=self.countMap.get(item)
                user=None
                if onLine==None:
                    user=User(fname[0][0],item,0)
                else:
                    user = User(fname[0][0],item, 1)
                fl.append(user)
        #
        #=pickle.dumps(fl)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"查询好友完成")
        pt=MyPotocol(POTOCOL.SADDFL,fl)
        pdata=pickle.dumps(pt)
        self.conn.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发送好友列表完成！")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"select * from Mess where des={0} order by idate asc".format(self.count))
        #print(self.count)
        li=MySQL.execute("select * from Mess where des={0} order by idate asc".format(self.count))
        #li=c.fetchall()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"查询离线信息查询完成")
        for item in li:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始反解析完毕")
            tpt=pickle.loads(item[4])
            tpt.data[POTOCOL.DATE] = item[5]
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"解析完毕:type={0}".format(item[3]))
            if item[3]==POTOCOL.MMESS:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}向{1}发送对话消息".format(item[1],item[2]),POTOCOL.LOGINFO)
                tpt.data[POTOCOL.INFOID] = item[0]
                pdata = pickle.dumps(tpt)
                self.conn.sendall(pdata)
                if self.date==None:
                    self.date=item[5]
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),item[5])
                pt=MyPotocol(POTOCOL.UMESS,{POTOCOL.RES:item[1],POTOCOL.DES:item[2],POTOCOL.MESS:item[4],POTOCOL.DATE:item[5]})
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始存入数据库")
                self.TalkIntoDB(pt)
            elif item[3]==POTOCOL.MINFO:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}向{1}发送通知消息".format(item[1],item[2]),POTOCOL.LOGINFO)
                tpt.data[POTOCOL.INFOID] = item[0]
                pdata = pickle.dumps(tpt)
                self.conn.sendall(pdata)
            elif item[3]==POTOCOL.MFILE:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}向{1}:id={2}发送文件消息".format(item[1],item[2],item[0]),POTOCOL.LOGINFO)
                tpt.pno = POTOCOL.SINFOFILE
                #file=tpt.data.get(POTOCOL.FILE)
                #tpt.data[POTOCOL.FILE]=file.filename
                tpt.data[POTOCOL.INFOID]=item[0]
                pdata = pickle.dumps(tpt)
                self.conn.sendall(pdata)
                pass
        #db=sqlite3.connect(POTOCOL.DBNAME)
        #c=db.cursor()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发送离线信息完成")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"清理离线消息开始..")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"delete from Mess where des={0} and type={1}".format(self.count,POTOCOL.MMESS))
        MySQL.execute("delete from Mess where des=%d and type=%d"%(int(self.count),int(POTOCOL.MMESS)))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"清理离线消息完成..")
        #db.commit()
        
        connres = self.countMap.get(self.count)
        # lock.release()

        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"InitChat完成！")
    def TalkIntoDB(self,pt):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始插入对话...")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(pt))
        data=pt.data
        count1=data.get(POTOCOL.RES)
        count2=data.get(POTOCOL.DES)
        mess=data.get(POTOCOL.MESS)
        date=data.get(POTOCOL.DATE)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"获取参数完成")
        #db=self.db
        #c=db.cursor()
        lockChat.acquire()
        id=Server.CHATID
        Server.CHATID+=1
        lockChat.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"获取参数完成")
        if date==None:
            date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            MySQL.execute("insert into chat(id,count1,count2,msg,idate) VALUES(?,?,?,?,?)",(id,count1,count2,mess,date))
        else:
            MySQL.execute("insert into chat VALUES (?,?,?,?,?)",(id,count1,count2,mess,date))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"插入对话完成...")
        return id
    def changeStaus(self,data):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"changeStaus start")
        li=self.getOnLineFriend()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"有%d个在线好友！"%(len(li)))
        pt=MyPotocol(POTOCOL.SCHSTAUS,{POTOCOL.COUNT:self.count,POTOCOL.STAUS:data})
        pdata=pickle.dumps(pt)
        #debug
        #for item in li.keys():
        #   print("向%d发起上线通知！"%item)
        for item in li.values():
            item.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"changeStaus end")
    def getOnLineFriend(self):
        li = self.getFriend()
        newLi=dict()
        for item in li:
            lock.acquire()
            conn=Server.countMap.get(item)
            lock.release()
            if conn!=None:
                newLi[item]=conn
        return newLi
    def getFriend(self):
        li=[]
        #db = self.db
        #c = db.cursor()
        res=MySQL.execute("select * from Friend where count1={0} or count2={0}".format(self.count))
        #res=c.fetchall()
        
        for item in res:
            if item[0]==self.count:
                li.append(item[1])
            else:
                li.append(item[0])
        return li
    def Register(self,data):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始注册！")
        username=data.data.get(POTOCOL.USERNAME)
        password=data.data.get(POTOCOL.PASSWORD)
        if username==None or password==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Register协议错误！",POTOCOL.LOGERROR)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"username:{0},password:{1}".format(username,password))
        lockCount.acquire()
        count=Server.COUNTBASE
        Server.COUNTBASE+=1
        lockCount.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"新账号：{0}".format(count))
        #db = self.db
        #c = db.cursor()
        try:
            MySQL.execute("insert into user VALUES (?,?,?)",(count,password,username))
        except:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"error:insert into user VALUES ('{0}','{1}','{2}')".format(count,password,username),POTOCOL.LOGERROR)
        #db.commit()
        
        pt=MyPotocol(POTOCOL.SRSUCCESS,{POTOCOL.COUNT:"{0}".format(count)})
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"注册成功")
        pdata=pickle.dumps(pt)
        self.conn.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"回复注册成功！")
    def Offline(self,data):
        pass

    def AddFriend(self,data):
        res=data.data.get(POTOCOL.RES)
        des=data.data.get(POTOCOL.DES)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}添加{1}申请为好友".format(res,des),POTOCOL.LOGINFO)
        lock.acquire()
        conn=Server.countMap.get(des)
        lock.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(des))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"进入查询阶段...")
        #db = self.db
        #c = db.cursor()
        li=MySQL.execute("select * from friend where (count1={0} and count2={1}) or (count1={1} and count2={0})".format(res,des))
        #li=c.fetchall()
        if len(li)>0:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}:{1}已经是好友！".format(res,des),POTOCOL.LOGINFO)
            pt = MyPotocol(POTOCOL.SMESSBOX,"你们已经是好友了！")
            pdata = pickle.dumps(pt)
            self.conn.sendall(pdata)
            return

        #print("select * from Mess where res={0} and des={1} and type={2}".format(res,des,POTOCOL.INFOADD))
        li=MySQL.execute("select * from Mess where res={0} and des={1} and type={2}".format(res,des,POTOCOL.INFOADD))
        if len(li)>0:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,
                                                    self.count), "{0}:{1}好友请求！".format(res, des), POTOCOL.LOGINFO)
            pt = MyPotocol(POTOCOL.SMESSBOX, "请不要重复提交好友申请！")
            pdata = pickle.dumps(pt)
            self.conn.sendall(pdata)
            return
        if conn==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始查询该账号是否存在")
            li=MySQL.execute("select * from user where count={0}".format(des))
            #li=c.fetchall()
            if len(li)<=0:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}好友不存在！".format(des),POTOCOL.LOGINFO)
                pt=MyPotocol(POTOCOL.UCOUNTERR,{POTOCOL.COUNT:des})
                pdata=pickle.dumps(pt)
                self.conn.sendall(pdata)
            else:
                pt = MyPotocol(POTOCOL.SADDF, {POTOCOL.COUNT: res})
                #pdata = pickle.dumps(pt)
                #c.execute("insert into Mess VALUES (?,?)", (des, sqlite3.Binary(pdata)))
                id=self.ToWater(c,self.count,des,POTOCOL.MINFO,pt)

        else:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"请求已发送！")
            pt = MyPotocol(POTOCOL.SADDF, {POTOCOL.COUNT: res})
            id=self.ToWater(c,self.count,des,POTOCOL.MINFO,pt)
            pdata = pickle.dumps(pt)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"插入完毕！")
            conn.sendall(pdata)

        pt = MyPotocol(POTOCOL.SMESSBOX, "好友申请已发送！")
        pdata = pickle.dumps(pt)
        self.conn.sendall(pdata)
        #db.commit()
        
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"AddFriend完成！")
    def DeleteFriend(self,pt):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"删除好友开始")
        count1=pt.data.get(POTOCOL.RES)
        count2=pt.data.get(POTOCOL.DES)
        self.Transpond(pt,POTOCOL.MINFO)
        conn=self.countMap.get(count2)
        MySQL.execute("delete from friend where count1={0} and count2={1} or count1={1} and count2={0}".format(count1,count2))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}删除了好友{1}".format(count1,count2))
    def ToWater(self,c,res,des,type,pt):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始记录流水")
        if type==POTOCOL.MINFO:
            li=MySQL.execute("select * from Mess where res={0} and des={1} and type={2}".format(res,des,type))
            #li=c.fetchall()
            if len(li)>0:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"[res={0}:des={1}:type={2}]该通知类消息已存在！".format(res,des,type),POTOCOL.LOGINFO)
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"记录流水完成！")
                return

        lockWater.acquire()
        id = Server.WATERID
        Server.WATERID += 1
        lockWater.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"id={0}".format(id))
        pt.data[POTOCOL.INFOID]=id
        pdata=pickle.dumps(pt)
        date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        MySQL.execute("insert into Mess(id,res,des,type,pt,idate) VALUES (?,?,?,?,?,?)", (id, res,des,type, sqlite3.Binary(pdata),date))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"流水执行完成")
        return id
    def AddUser(self,res,des):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发送添加用户开始")
        lock.acquire()
        connres = self.countMap.get(res)
        lock.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(res))
        if connres==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}不在线！".format(res),POTOCOL.LOGINFO)
            return
        user=self.getUser(des)
        if user==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}用户不存在".format(des),POTOCOL.LOGINFO)
            return
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"封装协议开始")
        pt = MyPotocol(POTOCOL.SADDUSER, {POTOCOL.USER: user})
        pdata = pickle.dumps(pt)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始发送...")
        connres.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发送{0}添加{1}用户完成".format(res,des))
    def getUser(self,count):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"获取用户开始")
        #c=self.db.cursor()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"select * from user where count={0}".format(count))
        li=MySQL.execute("select * from user where count={0}".format(count))
        #li=c.fetchall()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"获取用户完成")
        if len(li)<=0:
            return None
        else:
            user=User(count=li[0][0],username=li[0][2],isOnLine=1)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"返回数据")
            return user
        #lock.release()
        #Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"获取用户完成")
    def Refuse(self,data):
        reldata = data.data
        res = reldata[POTOCOL.RES]
        des = reldata[POTOCOL.DES]
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Agree start")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"res={0}".format(res))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(res))
        lock.acquire()
        connres = self.countMap.get(res)
        lock.release()
        if connres == None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"用户错误！")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}拒绝了{1}的好友请求...".format(res,des),POTOCOL.LOGINFO)
        self.Transpond(data,POTOCOL.MINFO)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发起拒绝结束...")
    def Agree(self,data):
        reldata=data.data
        res = reldata[POTOCOL.RES]
        des = reldata[POTOCOL.DES]
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Agree start")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"res={0}".format(res))
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(res))
        lock.acquire()
        connres = self.countMap.get(res)
        lock.release()
        if connres==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"用户错误！")

        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"发起同意...")
        #Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(self.user))
        #data.data[POTOCOL.USER]=self.user
        self.AddUser(res,des)
        self.AddUser(des,res)
        self.Transpond(data,POTOCOL.MINFO)
        #db=self.db
        #c=db.cursor()
        li=MySQL.execute("select * from friend where count1={0} and count2={1} or count1={1} and count2={0}".format(res,des))
        #li=c.fetchall()
        if len(li)<=0:
            MySQL.execute("INSERT INTO Friend  VALUES (?,?)",(res,des))
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"数据库操作：{0}成为{1}的好友".format(res,des),POTOCOL.LOGINFO)
        else:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}成为{1}已经是好友！".format(res,des),POTOCOL.LOGINFO)
        #c.execute("delete from Mess where id={0}".format())
        #db.commit()
    def SendWord(self,data):
        reldata=data.data
        res = reldata[POTOCOL.RES]
        des = reldata[POTOCOL.DES]
        li=MySQL.execute("select * from friend where count1={0} and count2={1} or count1={1} and count2={0}".format(res,des))
        if len(li)==0:
            pt=MyPotocol(POTOCOL.SMESSBOX,"发送失败！对方不是您的好友！")
            pdata=pickle.dumps(pt)
            self.conn.sendall(pdata)
            return
        self.Transpond(data)
    def Transpond(self,data,type=POTOCOL.MMESS):#记录并转发
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Transpond开始")
        reldata=data.data
        res=reldata[POTOCOL.RES]
        des=reldata[POTOCOL.DES]
        if res==None or des==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Transpond 协议错误！",POTOCOL.LOGERROR)
        res=int(res)
        des=int(des)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"res:{0},des:{1}".format(res,des))
        lock.acquire()
        connres=self.countMap.get(res)
        lock.release()
        if connres==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}请登陆！".format(res),POTOCOL.LOGERROR)
            pt=MyPotocol(POTOCOL.SMESSBOX,"请先登陆！")
            pickle.dump(pt,connres)
            return
        lock.acquire()
        conndes=self.countMap.get(des)
        lock.release()
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"参数检查完毕")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"链接数据库完成！")
        if conndes==None:
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"查询是否离线")
            li=MySQL.execute("select * from user where count={0}".format(des))
            #li=c.fetchall()
            if len(li)<=0:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"用户不存在")
                pt=MyPotocol(POTOCOL.SMESSBOX,"该用户不存在！")
                pdata=pickle.dumps(pt)
                connres.sendall(pdata)
                return -1
            else:
                Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"用户离线")
                return self.ToWater(c,self.count,des,type,data)

        id=-1
        if type==POTOCOL.MINFO:
            self.ToWater(c, self.count, des, type, data)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count), "{0}向{1}发送：{2}".format(res, des, type),POTOCOL.LOGINFO)
        elif type==POTOCOL.MMESS:
            msg=data.data.get(POTOCOL.MMESS)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}向{1}发送：{2}".format(res,des,msg),POTOCOL.LOGINFO)
            id=self.TalkIntoDB(data)
            li=MySQL.execute("select idate from chat where id={0}".format(id))
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),li[0][0])
            data.data[POTOCOL.DATE]=li[0][0]
        elif type==POTOCOL.MFILE:
            id=self.ToWater(c, self.count, des, type, data)
            li = MySQL.execute("select idate from Mess where id={0}".format(id))
            data.data[POTOCOL.DATE] = li[0][0]
            data.pno=POTOCOL.SINFOFILE
            file=data.data.get(POTOCOL.FILE)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"{0}向{1}发送文件：{2}".format(res,des,file.filename),POTOCOL.LOGINFO)
        pdata = pickle.dumps(data)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"正在发送给%d" % des)
        conndes.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"Transpond结束")
        return id
    def SendFileInfo(self,pt):
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始发送文件")
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),type(pt))
        #file=pt.data(POTOCOL.FILE)
        #filename = file.filename
        #pt.data[POTOCOL.FILE]=filename
        pdata = pickle.dumps(pt)
        self.conn.sendall(pdata)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count), "发送文件结束")
    def SendFile(self,pt):
        id = pt.data.get(POTOCOL.ID)
        Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"开始发送文件{0}".format(id))
        li=MySQL.execute("select * from Mess where id={0}".format(id))
        data=li[0][4]
        filepath="{1}/{0}.file".format(id,POTOCOL.PATHFILE)
        #print()

        file = open(filepath, "rb")
        print("打开文件{0}".format(filepath))
        pt=pickle.loads(data)
        #length=pt.data[POTOCOL.INFOFILE].file
        length=os.path.getsize(filepath)
        print(length)
        try:
            self.conn.sendall(data)
            while True:
                data=file.read(1024)
                data=pickle.dumps(data)
                self.conn.sendall(data)
                length-=len(data)
                print(length)
                if not data:
                    break
        except Exception as e:
            print(e)
            Log.Print("[{0}][{1}][{2}][{3}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno,self.count),"对方主动关闭了接收文件或异常掉线",POTOCOL.LOGERROR)
            if length<=0:
                print("发送成功")
            else:
                print("发送失败")
            return
        finally:
            #self.conn.close()
            if file !=None:
                file.close()
            MySQL.execute("delete from Mess where id={0}".format(id))
            print("文件已删除")

        #MySQL.execute("delete from Mess where id={0}".format(id))
        print("发送文件完毕")
    @staticmethod
    def isAlive():
        while True:
            time.sleep(10)
            Log.Print("[{0}][{1}][{2}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno),"心跳...")
            for item in Server.countMap.keys():
                pt=MyPotocol(POTOCOL.SALIVE)
                pdata=pickle.dumps(pt)
                lock.acquire()
                conn=Server.countMap.get(item)
                if conn==None:
                    lock.release()
                    continue
                try:
                    conn.sendall(pdata)
                    #fd=conn.makefile(mode="rwb")
                    #pt=pt.load(fd)
                except:
                    Server.countMap.pop(item)
                    Log.Print("[{0}][{1}][{2}]".format(__file__, sys._getframe().f_code.co_name, sys._getframe().f_lineno),"{0}已离线！".format(item))
                lock.release()
def process(conn,addr):
    Server(conn,addr)

db=sqlite3.connect(POTOCOL.DBNAME)
c=db.cursor()
c.execute("select max(count) from user")
li=c.fetchall()
if li[0][0]==None:
    Server.COUNTBASE=123
else:
    Server.COUNTBASE=li[0][0]+1
c.execute("select max(id) from Mess")
li=c.fetchall()

if li[0][0]==None:
    Server.WATERID=0
else:
    Server.WATERID=li[0][0]+1


c.execute("select max(id) from chat")

li=c.fetchall()
db.close()
if li[0][0]==None:
    Server.CHATID=0
else:
    Server.CHATID=li[0][0]+1
db.close()
lock=threading.Lock()
lockCount=threading.Lock()
lockWater=threading.Lock()
lockChat=threading.Lock()
sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind((POTOCOL.IP,POTOCOL.PORT))
sock.listen(128)
if not os.path.isdir(POTOCOL.PATHFILE):
    os.mkdir(POTOCOL.PATHFILE)
#t1=threading.Thread(target=Server.isAlive)
#t1.start()
while True:
    conn,addr=sock.accept()
    #conn.setblocking(False)
    t=threading.Thread(target=process,args=(conn,addr))
    t.start()