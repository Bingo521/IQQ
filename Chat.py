import socket
import sys
from POTOCOL import *
import pickle
import wx
import os
import threading
import time
def LoginSuccess(data):
    print("登陆成功，正在跳转至主界面！")
    wx.CallAfter(Chat.Frame.LoginSuccess)
def MessBox(pt):
    print("消息：{0}".format(pt.data))
    wx.CallAfter(Chat.Frame.MessBox,pt.data)
def MessageBox(pt):
    wx.CallAfter(Chat.Frame.MessBox, pt)
def CountErr(pt):
    count=pt.data.get(POTOCOL.COUNT)
    if count==None:
        print("CountErr")
    print("消息：{0}".format(count))
    wx.CallAfter(Chat.Frame.MessBox,"{0}该账号不存在！".format(count))
def DoNothing(pt):
    print("心跳...")
def Register(pt):
    print("注册成功，正在跳转至登陆界面")
    wx.CallAfter(Chat.Frame.RegisterSuccess, pt.data)
def JoinMe(pt):
    print("有好友请求...")
    #print("id=%d"%pt.data.get(POTOCOL.INFOID))
    wx.CallAfter(Chat.Frame.JoinMe, pt.data)
def addFlist(pt):
    print("初始化好友列表")
    wx.CallAfter(Chat.Frame.InitFList, pt.data)
def Agreed(pt):
    print("有好友同意")
    res=pt.data.get(POTOCOL.RES)
    des=pt.data.get(POTOCOL.DES)
    id=pt.data.get(POTOCOL.INFOID)
    #user=pt.data.get(POTOCOL.USER)
    print("id=%d"%pt.data.get(POTOCOL.INFOID))
    tip=dict()
    tip[POTOCOL.INFOTIP]="{0}同意您的好友请求".format(res)
    tip[POTOCOL.COUNT]=res
    tip[POTOCOL.INFOID]=id
    #tip[POTOCOL.USER]=user
    if res==None or des==None:
        print("Agreed：协议错误")
    wx.CallAfter(Chat.Frame.BeAgeed,tip)
def SeeHistory(data):

    pass
def Refuse(pt):
    print("有好友拒绝")
    res = pt.data.get(POTOCOL.RES)
    des = pt.data.get(POTOCOL.DES)
    id = pt.data.get(POTOCOL.INFOID)
    #user = pt.data.get(POTOCOL.USER)
    print("id=%d" % pt.data.get(POTOCOL.INFOID))
    tip = dict()
    tip[POTOCOL.INFOTIP] = "拒绝了您的好友请求"
    tip[POTOCOL.COUNT] = res
    tip[POTOCOL.INFOID] = id
    #tip[POTOCOL.USER] = user
    if res == None or des == None:
        print("Agreed：协议错误")
    wx.CallAfter(Chat.Frame.Inform, tip)
def ChangeStaus(pt):
    print("有好友上线")
    wx.CallAfter(Chat.Frame.ChangeStaus,pt.data)
def AddUser(pt):
    wx.CallAfter(Chat.Frame.AddUser,pt.data)
def GetWord(pt):
    print("获取对话")
    wx.CallAfter(Chat.Frame.GetWord, pt.data)
def InitSelf(pt):
    print("初始化用户")
    wx.CallAfter(Chat.Frame.InitSelf, pt.data)
def DeleteFriend(pt):
    print("好友删除通知")
    res = pt.data.get(POTOCOL.RES)
    des = pt.data.get(POTOCOL.DES)
    id = pt.data.get(POTOCOL.INFOID)
    # user = pt.data.get(POTOCOL.USER)
    #print("id=%d" % pt.data.get(POTOCOL.INFOID))
    tip = dict()
    tip[POTOCOL.INFOTIP] = "将您从好友列表中移除"
    tip[POTOCOL.COUNT] = res
    tip[POTOCOL.INFOID] = id
    # tip[POTOCOL.USER] = user
    if res == None or des == None:
        print("Agreed：协议错误")
    wx.CallAfter(Chat.Frame.Inform, tip)
def InfoFile(pt):
    wx.CallAfter(Chat.Frame.InfoFile, pt.data)
def recvOk(id):
    print("提示接收完成")
    wx.CallAfter(Chat.Frame.recvOk, id)
def SendFileInfo(data):
    wx.CallAfter(Chat.Frame.SendFileInfo,data)
    pass
def SendFileOk(data):
    wx.CallAfter(Chat.Frame.SendFileOk,data)
    pass
def Process(data):
    wx.CallAfter(Chat.Frame.MyProcess,data)
    pass
class Chat(object):
    conn=None
    fd=None
    chatWith = None
    Me = None
    Frame = None
    isConnect=False
    funcMap={
        POTOCOL.SSUCCESS:LoginSuccess,
        POTOCOL.SMESSBOX:MessBox,
        POTOCOL.SALIVE:DoNothing,
        POTOCOL.SRSUCCESS:Register,
        POTOCOL.UCOUNTERR:CountErr,
        POTOCOL.SADDF:JoinMe,
        POTOCOL.SADDFL:addFlist,
        POTOCOL.UAGREE:Agreed,
        POTOCOL.UREFUSE:Refuse,
        POTOCOL.SCHSTAUS:ChangeStaus,
        POTOCOL.SADDUSER:AddUser,
        POTOCOL.USENDWORD:GetWord,
        POTOCOL.SINITSELF:InitSelf,
        POTOCOL.UDELETEF:DeleteFriend,
        POTOCOL.SINFOFILE:InfoFile
    }
    def __init__(self):
        pass
    @staticmethod
    def run(Frame):
        Chat.Frame=Frame
        print("等待中...")
        while True:
            try:
                pt=pickle.load(Chat.fd)
                print(pt.pno)
                func=Chat.funcMap.get(pt.pno)
                if func!=None:
                    Chat.funcMap[pt.pno](pt)
                else:
                    print("协议未定义")
            except Exception as e:
                print(e)
                break
    @staticmethod
    def setChatWith(user):
        Chat.chatWith=user
    @staticmethod
    def Agree(count1,count2):
        pt=MyPotocol(POTOCOL.UAGREE,{POTOCOL.RES:count1,POTOCOL.DES:count2})
        pdata=pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        print("同意信息发送完毕")
    @staticmethod
    def DeleteId(id):
        pt=MyPotocol(POTOCOL.UDELETEID,{POTOCOL.ID,id})
        pdata=pickle.dumps(pt)
        Chat.conn.sendall(pdata)
    @staticmethod
    def setMe(user):
        Chat.Me=user

    @staticmethod
    def toLogIn(username,password):#登陆判断
        pt = MyPotocol(POTOCOL.ULOGIN, {POTOCOL.COUNT: username, POTOCOL.PASSWORD: password})
        data=pickle.dumps(pt)
        Chat.conn.sendall(data)
        print("发送登陆请求完成!")
    @staticmethod
    def toRegister(username,password):
        pt = MyPotocol(POTOCOL.UREGITSER, {POTOCOL.USERNAME: username, POTOCOL.PASSWORD: password})
        data = pickle.dumps(pt)
        Chat.conn.sendall(data)
        print("发送注册请求完成!")

    @staticmethod
    def toAddFriend(data):
        count=data.get(POTOCOL.COUNT)
        if count==None:
            print("toAddFriend协议错误")
            return
        if Chat.Me==None:
            print("请先登陆！")
            return
        pt=MyPotocol(POTOCOL.UADDF,{POTOCOL.DES:count,POTOCOL.RES:Chat.Me.count})
        print("{0}:{1},{2}:{3}".format(POTOCOL.RES,Chat.Me.count,POTOCOL.DES,count))
        pdata=pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        print("发送添加好友请求完成！")
        pass
    @staticmethod
    def send(msg):
        if Chat.chatWith==None:
            MessageBox("请先选择一个好友")
        print("开始发送消息")
        pt=MyPotocol(POTOCOL.USENDWORD,{POTOCOL.RES:Chat.Me.count,POTOCOL.DES:Chat.chatWith.count,POTOCOL.MESS:msg})
        pdata=pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        print("发送消息完成")
    @staticmethod
    def deleteFriend(user):
        pt=MyPotocol(POTOCOL.UDELETEF,{POTOCOL.RES:Chat.Me.count,POTOCOL.DES:user.count})
        pdata = pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        pass
    @staticmethod
    def Fefuse(count1,count2):
        pt = MyPotocol(POTOCOL.UREFUSE, {POTOCOL.RES: count1, POTOCOL.DES: count2})
        pdata = pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        print("同意信息发送完毕")
    @staticmethod
    def DeleteInfo(id):
        pt=MyPotocol(POTOCOL.UDELETEINFO,{POTOCOL.INFOID:id})
        pdata=pickle.dumps(pt)
        Chat.conn.sendall(pdata)
        print("删除已完成")

    @staticmethod
    def SendFile(path,filename):
        if not os.path.exists(path):
            MessageBox("未找到该文件！")
            return False
        if not os.path.isfile(path):
            MessageBox("该路径不是一个文件")
            return False
        print("开始发送文件")
        t=threading.Thread(target=Chat.SendFile2,args=(path,filename))
        t.daemon=True
        t.start()
        pass
    @staticmethod
    def SendFile2(path,filename):
        data=dict()
        id = time.time()
        data[POTOCOL.FILENAME]=filename
        data[POTOCOL.COUNT]=Chat.chatWith.count
        data[POTOCOL.INFOID]=id
        data[POTOCOL.PROCESS]=0
        data[POTOCOL.SPEED] = 0
        data[POTOCOL.INFOTIP]="[0%]正在向{0}发送{1}".format(Chat.chatWith.count,filename)
        item=Inform(POTOCOL.INFOSEND,data)
        SendFileInfo(item)
        tempConn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        print("链接成功！")
        try:
            tempConn.connect((POTOCOL.IP, POTOCOL.PORT))
            #print("123")
            tempfd = tempConn.makefile(mode="rwb")
            #content = file.read()
            #myfile=MyFile(filename,content)
            size=os.path.getsize(path)
            myfile = MyFile(filename, size)
            pt=MyPotocol(POTOCOL.USENDFILE,{POTOCOL.RES:Chat.Me.count,POTOCOL.DES:Chat.chatWith.count,POTOCOL.FILE:myfile})
            pdata=pickle.dumps(pt)
            tempConn.sendall(pdata)
            file = open(path, "rb")
            rel=size
            filelength=size
            print("size={0}".format(size))
            pre=time.time()
            speed=0
            while True:
                rtext=file.read(1024*10)
                #pt=Data(rtext)
                pdata=pickle.dumps(rtext)
                tempConn.sendall(pdata)
                l=len(pdata)
                filelength-=l
                speed+=l

                t=time.time()
                if t-pre>1:
                    if rel != 0:
                        if filelength < 0:
                            filelength = 0
                        data[POTOCOL.PROCESS] = (rel - filelength) / rel
                        # print(data[POTOCOL.PROCESS])
                    else:
                        data[POTOCOL.PROCESS] = 1
                    data[POTOCOL.ID] = id
                    print(t)
                    pre=t
                    data[POTOCOL.SPEED]=speed
                    speed=0
                    Process(data)
                if not rtext:
                    break

            file.close()
            #ok=tempConn.recv(10)
            #print(ok.decode())
            SendFileOk(id)
        except Exception as e:
            print(e)
        finally:
            tempConn.close()
            #sys.exit()


    @staticmethod
    def Recv(id,path):
        print("id={0}".format(id))
        t = threading.Thread(target=Chat.Recv2, args=(id, path))
        t.daemon=True
        t.start()
        pass
    @staticmethod
    def Recv2(id,path):
        tempConn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            tempConn.connect((POTOCOL.IP, POTOCOL.PORT))
            print("接收文件{0}链接成功！".format(id))
            tempfd = tempConn.makefile(mode="rwb")
            pt=MyPotocol(POTOCOL.UGETFILE,{POTOCOL.ID:id})
            pdata=pickle.dumps(pt)
            tempConn.sendall(pdata)

            pt=pickle.load(tempfd)
            file=pt.data.get(POTOCOL.FILE)
            filename=file.filename

            filelength=file.file
            rel=filelength
            print(filename,filelength)
            path=path+"/"+filename
            fd=None
            try:
                fd = open(path, "wb")
                print("文件打开完成")
                pre=time.time()
                speed=0
                while True:
                    data=pickle.load(tempfd)
                    fd.write(data)
                    length=len(data)
                    filelength-=length
                    speed+=length
                    #print(filelength)

                    t=time.time()
                    if t-pre>1:
                        print(t)
                        pre=t
                        data = dict()
                        if rel != 0:
                            data[POTOCOL.PROCESS] = (rel - filelength) / rel
                        else:
                            data[POTOCOL.PROCESS] = 1
                        data[POTOCOL.ID] = id
                        data[POTOCOL.SPEED]=speed
                        speed=0
                        Process(data)
                    if filelength<=0:
                        break
                    #print(len(data))
                print("接收完成")
                recvOk(id)
            except Exception as e:
                print(e)
                pass
            finally:
                if fd!=None:
                    fd.close()
                if tempConn!=None:
                    tempConn.close()
            print("接收完成")

        except Exception as e:
            print(e)
            #sys.exit()
        tempConn.close()

    @staticmethod
    def Connect(IP,PORT):
        if Chat.conn==None:
            Chat.conn=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            print("链接成功！")
            Chat.fd = Chat.conn.makefile(mode="rwb")
            try:
                Chat.conn.connect((POTOCOL.IP,POTOCOL.PORT))
            except:
                print("connect error!")
                sys.exit()
            Chat.isConnect=True

