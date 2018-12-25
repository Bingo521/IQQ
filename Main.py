import wx
#coding=utf-8
import wx
from POTOCOL import *
from Chat import Chat
import time
import threading
import sys
import os
class FriendListCtrl(wx.ListCtrl):
    def __init__(self, parent,size, id=-1, pos=(0, 0), style=wx.LC_SMALL_ICON| wx.LC_AUTOARRANGE):
        wx.ListCtrl.__init__(self, parent, id, pos, size, style)
        self.SetColumnWidth(1,-1)
        self.li=[]
    def InitImg(self,imgspath):
        self.Lenth=len(imgspath)
        imgs = wx.ImageList(45, 45, True)
        for path in imgspath:
            if not os.path.exists(path):
                print(path)
                path=POTOCOL.DEFAULTICO
            to_bmp_image = wx.Image(path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            imgs.Add(to_bmp_image)
        self.AssignImageList(imgs, wx.IMAGE_LIST_SMALL)
    def insert(self,users):
        index=0
        self.ClearAll()
        for item in users:
            print("插入:%d"%item.count)
            self.li.append(item)
        for index in range(len(self.li)-1,0,-1):#删除重复项
            u1=self.li[index]
            u2=self.li[index-1]
            if u1.count==u2.count:
                self.li.pop(index)
        sorted(self.li,key=lambda user:user.isOnLine)

        print("insert start")
        for item in self.li:
            print(item.isOnLine)
            snum=""
            num=item.ex.get(POTOCOL.MESSNUM)
            if num!=0:
                snum="({0})".format(num)
            text = u"{0}({1})             {2}".format(item.username, item.count,snum)
            self.InsertItem(index, text, item.isOnLine)
            index += 1
        print("insert end")
    def changeStaus(self,count,staus):
        for item in self.li:
            if item.count==count:
                item.isOnLine=staus
                break
        self.refresh()
    def GetUser(self,count):
        for item in self.li:
            if item.count==count:
                return item
        return None
        pass
    def GetById(self,id):
        for item in self.li:
            if item.data[POTOCOL.INFOID]==id:
                return item

    def SetIdValue2(self,id,key,value):
        print(value)
        for item in self.li:
            tid=item.data[POTOCOL.INFOID]
            if id==tid:
                item.data[key]=value
                break
        self.refresh2()
        pass
    def refresh(self):
        self.ClearAll()
        self.insert([])
    def refresh2(self):
        self.ClearAll()
        self.insert2([])
    def insert2(self,inform):
        self.ClearAll()
        index=0
        for item in inform:
            self.li.append(item)
        for item in self.li:
            type=1
            if item.type < self.Lenth:
                type = item.type
            tip = item.data.get(POTOCOL.INFOTIP)

            if tip == None:
                tip = ""
            self.InsertItem(index, tip, type)
            index += 1
    def deleteItem(self,index):
        item=self.li.pop(index)
        self.ClearAll()
        self.refresh2()
        return item
    def deleteItem1(self,index):
        item=self.li.pop(index)
        self.ClearAll()
        self.refresh()

        return item
class BasePanel(wx.Panel):
    def __init__(self, superior):
        self.base = superior.base
        psize = superior.GetSize()
        self.isize = (psize[0] - self.base[0], psize[1] - self.base[1])
        wx.Panel.__init__(self, parent=superior, size=self.isize)
        self.SetBackgroundColour("White")

class LoginPanel(BasePanel):
    def __init__(self,superior):
        BasePanel.__init__(self,superior)
        image_file = "img/login.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        self.username=wx.TextCtrl(self.bitmap,-1,size=(150,25))
        self.username.SetValue("请输入用户名")
        self.password = wx.TextCtrl(self.bitmap, -1,style=wx.TE_PASSWORD,size=(150,25))
        self.password.SetValue("请输入密码")
        self.username.SetPosition((self.isize[0]/2-80,self.isize[1]/2-30-5))
        self.password.SetPosition((self.isize[0] / 2 - 80, self.isize[1] / 2 + 30-5))
        bmp = wx.Image("img/loginBtn1.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.Login = wx.BitmapButton(self.bitmap, -1, bmp,
                                      pos=((self.isize[0] / 2 - 50-35, self.isize[1] / 2 + 90)),
                                      size=(70, 26))
        bmp = wx.Image("img/register.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.Register = wx.BitmapButton(self.bitmap, -1, bmp,
                                     pos=((self.isize[0] / 2 - 50-35+90, self.isize[1] / 2 + 90)),
                                     size=(70, 26))
class RegisterPanel(BasePanel):
    def __init__(self,superior):
        BasePanel.__init__(self,superior)
        image_file = "img/login.jpg"
        base=0
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        self.username=wx.TextCtrl(self.bitmap,-1,size=(150,25))
        self.password = wx.TextCtrl(self.bitmap, -1,style=wx.TE_PASSWORD,size=(150,25))
        self.conform=wx.TextCtrl(self.bitmap, -1, style=wx.TE_PASSWORD, size=(150, 25))
        self.username.SetPosition((self.isize[0]/2-80,self.isize[1]/2-30-5+base))
        self.password.SetPosition((self.isize[0] / 2 - 80, self.isize[1] / 2 -5+base))
        self.conform.SetPosition((self.isize[0] / 2 - 80, self.isize[1] / 2 + 30-5+base))
        self.username.SetValue("请输入昵称")
        bmp = wx.Image("img/register.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.Rigister = wx.BitmapButton(self.bitmap, -1, bmp,
                                      pos=((self.isize[0] / 2 - 50-35, self.isize[1] / 2 + 60+base)),
                                      size=(70, 26))
        bmp = wx.Image("img/back.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.Back = wx.BitmapButton(self.bitmap, -1, bmp,
                                     pos=((self.isize[0] / 2 - 50-35+90, self.isize[1] / 2 + 60+base)),
                                     size=(70, 26))
class FrendListPanel(BasePanel):
    def __init__(self, superior):
        BasePanel.__init__(self, superior)
        image_file = "img/com.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))

        li=[]
        self.textFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.friendList = FriendListCtrl(parent=self.bitmap,size=(self.isize[0],self.isize[1]-200), pos=(0,85))
        self.friendList.SetFont(self.textFont)
        self.friendList.SetBackgroundColour('#ffffff')
        self.friendList.InitImg(POTOCOL.OFFONICO)
        self.friendList.insert(li)
        self.label = wx.StaticText(self.bitmap, pos=(30, 10), size=(320, 30), id=-1, style=wx.ALIGN_CENTER)
        self.label.SetBackgroundColour("rgb(51,153,254)")
        font = wx.Font(20, wx.SCRIPT, wx.SLANT, wx.NORMAL, underline=False, faceName="楷体",
                       encoding=wx.FONTENCODING_DEFAULT)
        self.label.SetFont(font)
        self.label.SetLabel("好友列表")



class chatPanel(wx.Panel):
    def __init__(self,super):
        psize = super.GetSize()
        wx.Panel.__init__(self, parent=super,size=psize)
        self.isize=psize
        image_file = "img/com.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        isize=self.GetSize()
        self.chatMsgBox=wx.TextCtrl(self.bitmap,pos=(0,85),size=(self.isize[0],self.isize[1]-400),style=wx.TE_MULTILINE)
        self.sendBox=wx.TextCtrl(self.bitmap,pos=(0,self.isize[1]-400),size=(isize[0],200),style=wx.TE_MULTILINE)


class MsgListPanel(BasePanel):
    def __init__(self, superior):
        BasePanel.__init__(self, superior)
        image_file = "img/com.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        self.chatMsgBox = wx.TextCtrl(self.bitmap, pos=(0, 85), size=(self.isize[0], self.isize[1] - 300),
                                      style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.sendBox = wx.TextCtrl(self.bitmap, pos=(0, self.isize[1] - 400+85+100), size=(self.isize[0], 80+6),
                                   style=wx.TE_MULTILINE)
        self.label=wx.StaticText(self.bitmap,pos=(30,10),size=(320,30),id=-1,style=wx.ALIGN_CENTER)
        self.label.SetBackgroundColour("rgb(51,153,254)")
        font=wx.Font(20, wx.SCRIPT, wx.SLANT, wx.NORMAL, underline=False,faceName="楷体", encoding=wx.FONTENCODING_DEFAULT)
        self.label.SetFont(font)
        self.label.SetLabel("对话框")
        self.username = wx.StaticText(self.bitmap, pos=(0, 50), size=(370, 30), id=-1, style=wx.ALIGN_CENTER)
        self.username.SetBackgroundColour("rgb(51,153,254)")
        font = wx.Font(13, wx.SCRIPT, wx.SLANT, wx.NORMAL, underline=True, faceName="楷体",
                       encoding=wx.FONTENCODING_DEFAULT)
        self.username.SetFont(font)
        self.username.SetLabel("")
        bmp = wx.Image("img/left.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.sendFile = wx.BitmapButton(self.bitmap, -1, bmp,
                                     pos=((0, self.isize[1] - 400+85+200-20+6)),
                                     size=(190, 72))
        bmp = wx.Image("img/right.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.send = wx.BitmapButton(self.bitmap, -1, bmp,
                                     pos=((190, self.isize[1] - 400 + 85 + 200 - 20 + 6)),
                                     size=(190, 72))

class AddPanel(BasePanel):
    def __init__(self, superior):
        BasePanel.__init__(self, superior)
        image_file = "img/configback2.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        self.count=wx.TextCtrl(self,-1,pos=((self.isize[0]/2-40-100,self.isize[1]/2)),size=(200,25))
        bmp = wx.Image("img/send.jpg", wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.send = wx.BitmapButton(self, -1, bmp,
                                     pos=((self.isize[0]/2+90,self.isize[1]/2+2)),
                                     size=(20, 20))

class InformPanel(BasePanel):
    def __init__(self, superior):
        BasePanel.__init__(self, superior)
        image_file = "img/com.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))

        li=[]

        self.textFont = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.friendList = FriendListCtrl(self.bitmap, size=(self.isize[0], self.isize[1] - 200), pos=(0, 85))
        self.friendList.SetFont(self.textFont)
        self.friendList.SetBackgroundColour('#ffffff')
        self.friendList.InitImg(POTOCOL.INFOICO)
        self.friendList.insert(li)
        self.label = wx.StaticText(self.bitmap, pos=(30, 10), size=(320, 30), id=-1, style=wx.ALIGN_CENTER)
        self.label.SetBackgroundColour("rgb(51,153,254)")
        font = wx.Font(20, wx.SCRIPT, wx.SLANT, wx.NORMAL, underline=False, faceName="楷体",
                       encoding=wx.FONTENCODING_DEFAULT)
        self.label.SetFont(font)
        self.label.SetLabel("通知列表")

class ConfigPanel(BasePanel):
    def __init__(self, superior):
        BasePanel.__init__(self, superior)
        image_file = "img/configback.jpg"
        to_bmp_image = wx.Image(image_file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap = wx.StaticBitmap(self, -1, to_bmp_image, (0, 0))
        self.label = wx.StaticText(self, pos=(self.isize[0] / 2 - 40 - 160, self.isize[1] / 2+5), size=(40, 30), id=-1, style=wx.ALIGN_RIGHT)
        self.label.SetLabel("下载路径")
        self.path=sys.path[0]
        path=sys.path[0]+"/"+POTOCOL.STOREPATH
        fd=open(path,"r")
        relpath=fd.read()
        fd.close()
        self.pathLabel = wx.TextCtrl(self, -1, pos=((self.isize[0] / 2 - 40 - 100, self.isize[1] / 2)),
                                 size=(300, 25),style=wx.TE_READONLY)
        self.pathLabel.SetValue(relpath)
        self.config = wx.Button(self, -1,
                                    pos=((self.isize[0] / 2 + 180, self.isize[1] / 2 -2)),
                                    size=(30, 30),label="...")

class MainFrame(wx.Frame):
    def __init__(self,superior):
        wx.Frame.__init__(self,parent=superior,
                          title=u"IQQ",
                          size=(500,400),
                          style=(wx.DEFAULT_FRAME_STYLE^(wx.RESIZE_BORDER|wx.MAXIMIZE_BOX)))
        self.initFile()
        self.base=(0,0)
        self.LoginPanel=LoginPanel(self)
        self.Bind(wx.EVT_BUTTON,self.OnLogin,self.LoginPanel.Login)
        self.Bind(wx.EVT_BUTTON, self.OnRegister, self.LoginPanel.Register)
        self.allPanel=[]
        self.allPanel.append(self.LoginPanel)
        self.friendPanel = None
        self.chatPanel = None
        self.addPanel = None
        self.informPanel = None
        self.Register = None
        self.configPanel=None
        self.MessMap=dict()
        self.popMenu=dict()
        self.MessCount = [0, 0, 0, 0, 0]
        self.MessString = ["好友列表", "消息列表", "添加好友", "通知列表", "设置"]
        self.nowPos = 0
        menu=wx.Menu()
        menu.Append(901,"同意")
        menu.Append(902, "拒绝")
        menu.Append(903, "忽略")
        self.Bind(wx.EVT_MENU, self.Agree, id=901)
        self.Bind(wx.EVT_MENU, self.Fefuse, id=902)
        self.Bind(wx.EVT_MENU, self.DeleteInfo, id=903)
        self.popMenu[POTOCOL.INFOADD]=menu
        menu = wx.Menu()
        menu.Append(911, "删除")
        self.Bind(wx.EVT_MENU, self.DeleteInfo, id=911)
        self.popMenu[POTOCOL.INFO] = menu

        menu = wx.Menu()
        menu.Append(931, "接收")
        menu.Append(932, "忽略")
        self.Bind(wx.EVT_MENU, self.Recv, id=931)
        self.Bind(wx.EVT_MENU, self.DeleteInfo, id=932)
        self.popMenu[POTOCOL.INFOFILE] = menu
        menu = wx.Menu()
        menu.Append(921, "聊天")
        menu.Append(922, "删除该好友")
        self.Bind(wx.EVT_MENU, self.SelectFriend, id=921)
        self.Bind(wx.EVT_MENU, self.DeleteFriend, id=922)
        self.popMenu[POTOCOL.FMENU] = menu

        menu = wx.Menu()
        menu.Append(941, "删除")
        self.Bind(wx.EVT_MENU, self.DeleteInfo2, id=941)
        self.popMenu[POTOCOL.INFORECVOK] = menu

        self.msgMenu=wx.Menu()
        menu.Append(951, "查看历史")
        self.Bind(wx.EVT_MENU, self.SeeHistory, id=951)

        self.Init()


        try:
            Chat.Connect(POTOCOL.IP, POTOCOL.PORT)
        except:

            return
        t = threading.Thread(target=Chat.run, args=(self,))
        t.daemon=True
        t.start()
    def SeeHistory(self,event):
        print("see")
        data=dict()
        Chat.SeeHistory(data)
        pass
    def initFile(self):
        self.path=sys.path[0]
        print(self.path)
        self.storepath=self.path+"/"+POTOCOL.STOREPATH
        if not os.path.exists(self.storepath):
            fd=open(self.storepath,"w")
            fd.write(self.path)
            fd.close()
    def InitSelf(self,data):
        self.user=data.get(POTOCOL.USER)
        self.SetTitle("{0}({1})".format(self.user.username,self.user.count))
    def SelectFriend(self,event):
        user=self.friendPanel.friendList.li[self.index]
        Chat.setChatWith(user)
        self.chatPanel.username.SetLabel("{0}({1})".format(user.username,user.count))
        self.ShowMsgPanel()
        pass
    def DeleteFriend(self,event):
        user = self.friendPanel.friendList.li[self.index]
        isOk=wx.MessageBox("确定您要删除%s(%d)"%(user.username,user.count),"提示",wx.OK|wx.CANCEL,parent=self)
        if isOk==wx.OK:
            self.friendPanel.friendList.deleteItem1(self.index)
            print("发送删除信息！")
            Chat.deleteFriend(user)
    def Agree(self,event):
        item=self.informPanel.friendList.li[self.index]
        count=item.data.get(POTOCOL.COUNT)
        if count==None:
            print("Agree:协议错误...")
        Chat.Agree(int(self.count),int(count))
        self.DeleteInfo()
        print("已发送同意请求")
        print("删除该行")
    def DeleteId(self,id):
        Chat.DeleteId(id)
    def Fefuse(self,event):
        item = self.informPanel.friendList.li[self.index]
        count = item.data.get(POTOCOL.COUNT)
        if count == None:
            print("Refuse:协议错误...")
        self.DeleteInfo()
        Chat.Fefuse(int(self.count), int(count))
        print("已发送拒绝通知")
        print("删除该行")
    def DeleteInfo(self,event=0):
        print("开始删除")
        item=self.informPanel.friendList.li.pop(self.index)
        self.informPanel.friendList.refresh2()

        print("删除完毕")
        id = item.data.get(POTOCOL.INFOID)
        if id==None:
            print("id=====none")
            return
        Chat.DeleteInfo(id)
    def DeleteInfo2(self,event=0):
        print("开始删除")
        item = self.informPanel.friendList.li.pop(self.index)
        self.informPanel.friendList.refresh2()

        print("删除完毕")

    def OnShowLongin(self,event=0):
        self.Clear()
        self.SetSize((500,400))
        self.LoginPanel.Show(True)
    def OnLogin(self,event):
        if not Chat.isConnect:
            wx.MessageBox("服务器未正常运行！", "提示", wx.OK, self)
            return
        #校验登陆成功
        try:
            username=int(self.LoginPanel.username.GetValue())
            password=self.LoginPanel.password.GetValue()
            Chat.toLogIn(username, password)

        except:
            wx.MessageBox("用户名密码不合法", "提示", wx.OK, self)
        #隐藏登陆，添加菜单，显示好友列表
    def OnRegister(self,event):
        if not Chat.isConnect:
            wx.MessageBox("服务器未正常运行！", "提示", wx.OK, self)
            return

        self.Clear()

        if self.Register == None:
            print("已跳转至注册界面")
            self.Register = RegisterPanel(self)
            self.Bind(wx.EVT_BUTTON,self.OnShowLongin,self.Register.Back)
            self.Bind(wx.EVT_BUTTON,self.ToRegister,self.Register.Rigister)
            self.allPanel.append(self.Register)
        self.Register.Show(True)
    def ToRegister(self,event):
        username=self.Register.username.GetValue()
        password=self.Register.password.GetValue()
        conform=self.Register.conform.GetValue()
        print("password:{0},conform:{1}".format(password,conform))
        if password!=conform:
            wx.MessageBox("密码不一致！","提示！",wx.OK,self)
            return
        lenu=len(username)
        lenp=len(password)
        if lenu<=0:
            wx.MessageBox("用户名长度过短，请重新输入！", "提示！", wx.OK, self)
            return
        if lenu>16:
            wx.MessageBox("用户名长度过长，请重新输入！", "提示！", wx.OK, self)
            return
        if lenp<4:
            wx.MessageBox("密码长度过短，请重新输入！", "提示！", wx.OK, self)
            return
        if lenp>20:
            wx.MessageBox("密码长度过长，请重新输入！", "提示！", wx.OK, self)
            return
        Chat.toRegister(username,password)
    def RegisterSuccess(self,pt):
        count=pt.get(POTOCOL.COUNT)
        if count==None:
            print("RegisterSuccess协议错误！")
        self.LoginPanel.username.SetValue(str(count))
        self.OnShowLongin()
    def LoginSuccess(self):
        self.count=int(self.LoginPanel.username.GetValue())
        Chat.setMe(User("",self.count))
        self.LoginPanel.Show(False)
        #在此初始化
        self.menuBar = wx.MenuBar()
        self.friendList = wx.Menu()
        self.friendList.Append(100, "好友列表")
        self.menuBar.Append(self.friendList, "好友列表")
        self.msgList = wx.Menu()
        self.msgList.Append(200, "消息列表")
        self.menuBar.Append(self.msgList, "消息列表")
        self.addFriend = wx.Menu()
        self.addFriend.Append(300, "添加好友")
        self.menuBar.Append(self.addFriend, "添加好友")
        self.notifiList = wx.Menu()
        self.notifiList.Append(400, "通知列表")
        self.menuBar.Append(self.notifiList, "通知列表")
        self.friendList = wx.Menu()

        self.friendList.Append(500, "设置")
        self.menuBar.Append(self.friendList, "设置")
        self.SetMenuBar(self.menuBar)




        self.Bind(wx.EVT_MENU, self.ShowFriendList, id=100)
        self.Bind(wx.EVT_MENU, self.ShowMsgPanel, id=200)
        self.Bind(wx.EVT_MENU, self.ShowAddPanel, id=300)
        self.Bind(wx.EVT_MENU, self.ShowInformPanel, id=400)
        self.Bind(wx.EVT_MENU, self.ShowConfigPanel, id=500)
        self.ShowFriendList()

        self.timer = wx.Timer(self)  # 创建定时器
        self.Bind(wx.EVT_TIMER, self.Timer, self.timer)
        self.timer.Start(400)
    def Init(self):


        self.ShowFriendList()
        self.ShowAddPanel()
        self.ShowInformPanel()
        self.ShowMsgPanel()
        self.ShowConfigPanel(0)
        self.OnShowLongin()
        pass
    def ShowFriendList(self,event=0):
        self.nowPos=0
        self.MessCount[POTOCOL.FRIENDLIST]=0

        print("已跳转至好友列表")
        self.Clear()
        self.SetSize((385,780))
        if self.friendPanel==None:

            self.friendPanel = FrendListPanel(self)
            self.allPanel.append(self.friendPanel)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.ClickFlist, self.friendPanel.friendList)
        self.friendPanel.Show(True)
    def ClickFlist(self,event):
        self.index=event.GetIndex()
        self.informPanel.PopupMenu(self.popMenu[POTOCOL.FMENU])
    def ShowMsgPanel(self,event=0):
        self.nowPos=1
        self.MessCount[POTOCOL.MESSLIST]=0
        if Chat.chatWith!=None:
            user=self.friendPanel.friendList.GetUser(Chat.chatWith.count)
            if user!=None:
                user.ex[POTOCOL.MESSNUM]=0
            self.friendPanel.friendList.refresh()
        print("已跳转至消息列表")
        self.Clear()
        self.SetSize((385,780))
        if self.chatPanel==None:
            self.chatPanel = MsgListPanel(self)
            self.allPanel.append(self.chatPanel)
            self.Bind(wx.EVT_BUTTON,self.sendMsg,self.chatPanel.send)
            self.Bind(wx.EVT_BUTTON, self.sendFile, self.chatPanel.sendFile)
            self.Bind(wx.EVT_RIGHT_DOWN,self.ShowMsgMenu,self.chatPanel.bitmap)
        self.UpdateValue()
        self.chatPanel.Show(True)
    def ShowMsgMenu(self,event):
        print(123)
        self.PopupMenu(self.msgMenu)
        pass
    def sendFile(self,event):
        if Chat.chatWith==None:
            wx.MessageBox("请选择一位好友","提示",parent=self)
            return
        dlg=wx.FileDialog(self,u"请选择文件")
        if dlg.ShowModal() == wx.ID_OK:
            path=dlg.GetPath()
            filename=dlg.GetFilename()
            Chat.SendFile(path,filename)

    def UpdateValue(self):
        if Chat.chatWith==None:
            return
        msg=self.MessMap.get(Chat.chatWith.count)
        if msg==None:
            return
        self.chatPanel.chatMsgBox.SetValue(msg)
    def sendMsg(self,event):
        msg=self.chatPanel.sendBox.GetValue()
        self.chatPanel.sendBox.SetValue("")
        print("我说:{0}".format(msg))
        if Chat.chatWith==None:
            wx.MessageBox("请选择一位好友！","提示",wx.OK,self)
            return
        Chat.send(msg)
        date=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.SetWord(Chat.chatWith.count,date,msg,"我说")
    def GetWord(self,data):

        res=data.get(POTOCOL.RES)
        des=data.get(POTOCOL.DES)
        msg=data.get(POTOCOL.MESS)
        date=data.get(POTOCOL.DATE)
        if self.nowPos!=POTOCOL.MESSLIST and Chat.chatWith!=None and Chat.chatWith.count==res:
            self.MessCount[POTOCOL.MESSLIST]=1
        elif self.nowPos!=POTOCOL.FRIENDLIST and (Chat.chatWith==None or Chat.chatWith.count!=res):
            self.MessCount[POTOCOL.FRIENDLIST] = 1
        if Chat.chatWith==None or res!=Chat.chatWith.count or self.nowPos!=POTOCOL.MESSLIST:
            user=self.friendPanel.friendList.GetUser(res)
            user.ex[POTOCOL.MESSNUM]+=1
            self.friendPanel.friendList.refresh()
        self.SetWord(res,date,msg,"对方说:")
    def SetWord(self,res,date,msg,tip):
        relMsg = "{0}\r\n{1}：{2}\r\n\r\n".format(date, tip,msg)
        lock.acquire()
        mess = self.MessMap.get(res)
        if mess == None:
            self.MessMap[res] = relMsg
        else:
            self.MessMap[res] += relMsg
        if Chat.chatWith!=None and Chat.chatWith.count==res:
            self.chatPanel.chatMsgBox.SetValue(self.MessMap[res])
        lock.release()
        self.chatPanel.chatMsgBox.ShowPosition(self.chatPanel.chatMsgBox.GetLastPosition())
    def SendFileInfo(self,data):
        self.informPanel.friendList.insert2([data,])
        pass
    def ShowAddPanel(self,event=0):
        self.nowPos=2
        self.MessCount[POTOCOL.ADDLIST]=0
        print("已跳转至添加好友")
        self.Clear()
        self.SetSize((500,400))
        if self.addPanel==None:
            self.addPanel = AddPanel(self)
            self.allPanel.append(self.addPanel)
            self.Bind(wx.EVT_BUTTON,self.AddFriend,self.addPanel.send)
        self.addPanel.Show(True)
    def AddFriend(self,event=0):
        count=self.addPanel.count.GetValue()

        if len(count)==0 :
            wx.MessageBox("请输入好友账号！","提示",wx.OK,self)
            return
        count=int(count)
        if count==self.count:
            wx.MessageBox("不能添加自己为好友","提示",wx.OK,self)
            return
        try:
            count=int(count)
        except:
            wx.MessageBox("输入账号不合法！", "提示", wx.OK, self)
            return
        print("请求发送中...")
        Chat.toAddFriend({POTOCOL.COUNT:count})
        #wx.MessageBox("好友请求已发送！", "提示", wx.OK, self)
    def ShowInformPanel(self,event=0):
        self.nowPos=3
        self.MessCount[POTOCOL.INFOLIST]=0
        print("已跳转至通知列表")
        self.Clear()
        self.SetSize((385, 780))
        if self.informPanel == None:
            self.informPanel = InformPanel(self)
            self.allPanel.append(self.informPanel)
            self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.MybomChoose, self.informPanel.friendList)
        self.informPanel.Show(True)
    def ShowConfigPanel(self,event):
        self.nowPos = 4
        self.MessCount[POTOCOL.CONTROL] = 0
        print("已跳转至通知列表")
        self.Clear()
        self.SetSize((500, 400))
        if self.configPanel == None:
            self.configPanel = ConfigPanel(self)
            self.allPanel.append(self.configPanel)
            self.Bind(wx.EVT_BUTTON, self.SetPath, self.configPanel.config)
        self.configPanel.Show(True)
    def SetPath(self,event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            path=dlg.GetPath()
            self.configPanel.pathLabel.SetValue(path)
            fd=open(self.storepath,"w")
            fd.write(path)
            fd.close()
        pass
    def MybomChoose(self,event):
        self.index=event.GetIndex()
        item=self.informPanel.friendList.li[self.index]
        menu=self.popMenu.get(item.type)
        if menu!=None:
            self.informPanel.PopupMenu(menu)
        else:
            print("不能对该消息操作...")
    def MessBox(self,mess):
        wx.MessageBox(mess,"提示",wx.OK,self)
    def JoinMe(self,data):
        if self.nowPos!=POTOCOL.INFOLIST:
            self.MessCount[POTOCOL.INFOLIST]=1
        count=data.get(POTOCOL.COUNT)
        id=data.get(POTOCOL.INFOID)
        if count==None:
            print("JoinMe：协议错误！")
            return
        tip="{0}有好友请求".format(count)
        self.informPanel.friendList.insert2([Inform(POTOCOL.INFOADD,{POTOCOL.COUNT:count,POTOCOL.INFOID:id,POTOCOL.INFOTIP:tip}),])
    def BeAgeed(self,data):
        print("BeAgreed start")
        self.Inform(data)
        #user=data.get(POTOCOL.USER)
        #if user==None:
        #    print("BeAgreed:error")
        #self.friendPanel.friendList.insert([user,])
        print("BeAgreed end")
    def AddUser(self,data):
        print("AddUser start")
        user=data.get(POTOCOL.USER)
        if user==None:
           print("BeAgreed:error")
        user.ex[POTOCOL.MESSNUM]=0
        self.friendPanel.friendList.insert([user,])
        print("AddUser end")
    def Inform(self, data):
        if self.nowPos!=POTOCOL.INFOLIST:
            self.MessCount[POTOCOL.INFOLIST]=1
        tip=data.get(POTOCOL.INFOTIP)
        if tip == None:
            print("count：协议错误！")
            return
        self.informPanel.friendList.insert2([Inform(POTOCOL.INFO, data), ])
    def InfoFile(self,data):
        if self.nowPos!=POTOCOL.INFOLIST:
            self.MessCount[POTOCOL.INFOLIST]=1
        print("文件消息")
        res=data.get(POTOCOL.RES)
        des=data.get(POTOCOL.DES)
        file=data.get(POTOCOL.FILE)
        filename=file.filename
        length=file.file

        date=data.get(POTOCOL.DATE)
        id=data.get(POTOCOL.INFOID)
        if res==None or des==None or filename==None or date==None or id==None:
            print("res={0},des={1},filename={2},date={3},id={4}".format(res,des,filename,date,id))
            print("协议错误")
            return
        dat=dict()
        dat[POTOCOL.COUNT]=res
        dat[POTOCOL.FILENAME]=filename
        dat[POTOCOL.INFOTIP]="{2}向您发送了文件:{0}  日期:{1}".format(filename,date,res)
        dat[POTOCOL.INFOID]=id
        dat[POTOCOL.FILELEN]=length
        self.informPanel.friendList.insert2([Inform(POTOCOL.INFOFILE, dat), ])
        print("文件消息结束")
    def Recv(self,event):
        data=self.informPanel.friendList.li[self.index]
        data.data[POTOCOL.INFOTIP]="[1]{0}正在接收...".format(data.data[POTOCOL.FILENAME],0)
        data.data[POTOCOL.COUNT]=""
        data.type=POTOCOL.INFORECV
        id=data.data[POTOCOL.INFOID]
        self.informPanel.friendList.refresh2()
        path=self.configPanel.pathLabel.GetValue()
        Chat.Recv(id,path)
        pass
    def recvOk(self,id):
        for index in range(0,len(self.informPanel.friendList.li)):
            item=self.informPanel.friendList.li[index]
            tid=item.data.get(POTOCOL.INFOID)
            if tid!=None and tid==id:
                #self.countMap[self.]
                item.data[POTOCOL.INFOTIP]="{0}接收成功！".format(item.data[POTOCOL.FILENAME])
                item.type=POTOCOL.INFORECVOK
                print("修改完毕...")
                break
        self.informPanel.friendList.refresh2()
    def SendFileOk(self,id):
        for index in range(0,len(self.informPanel.friendList.li)):
            item=self.informPanel.friendList.li[index]
            tid=item.data.get(POTOCOL.INFOID)
            if tid!=None and tid==id:
                #self.countMap[self.]
                item.data[POTOCOL.INFOTIP]="{0}发送成功！".format(item.data[POTOCOL.FILENAME])
                item.type=POTOCOL.INFOSENDOK
                print("修改完毕...")
                break
        self.informPanel.friendList.refresh2()
    def InitFList(self,data):
        print("好友个数为：%d"%len(data))
        for item in data:
            item.ex[POTOCOL.MESSNUM]=0
        self.friendPanel.friendList.insert(data)
        print("初始化好友列表完成...")
    def ChangeStaus(self,data):
        count=data.get(POTOCOL.COUNT)
        staus=data.get(POTOCOL.STAUS)
        if count==None or staus==None:
            print("ChangeStaus:协议错误")
            return
        self.friendPanel.friendList.changeStaus(count,staus)
    def MyProcess(self,data):
        id=data[POTOCOL.ID]
        pro=data[POTOCOL.PROCESS]
        item=self.informPanel.friendList.GetById(id)
        speed=data[POTOCOL.SPEED]
        tip=""
        if item.type==POTOCOL.INFOSEND:
            tip="[%.2f%%  %.2fMB/s]正在向{0}发送{1}".format(item.data[POTOCOL.COUNT],item.data[POTOCOL.FILENAME])%(pro*100,speed/(1024*1024))
        else:
            tip="[%.2f%%  %.2fMB/s]{0}正在接收...".format(item.data[POTOCOL.FILENAME],pro)%(pro*100,speed/(1024*1024))
        print(tip)
        item.data[POTOCOL.INFOTIP]=tip
        self.informPanel.friendList.refresh2()
        #self.informPanel.friendList.SetIdValue2(id,POTOCOL.INFOTIP,tip)
        pass
    def Timer(self,event):
        #while True:
            #time.sleep(0.4)
        try:
            for index in range(0,len(self.MessCount)):
                #print("{0}:{1}".format(index,self.MessCount[index]))
                if  self.MessCount[index]!=0:
                    str=self.menuBar.GetMenuLabel(index)
                    if str!=self.MessString[index]:
                        self.menuBar.SetMenuLabel(index,self.MessString[index])
                    else:
                        self.menuBar.SetMenuLabel(index, "            ")
                else:
                    str = self.menuBar.GetMenuLabel(index)
                    #print("str=%s"%str)
                    #print(str != self.MessString[index])
                    if str != self.MessString[index]:

                        self.menuBar.SetMenuLabel(index, self.MessString[index])
        except Exception as e:
            print(e)
            pass
            #break
        #self.informPanel.friendList.insert([])
    def Clear(self):
        for item in self.allPanel:
            item.Show(False)
lock=threading.Lock()
if __name__=='__main__':
    app=wx.App()
    frame=MainFrame(None)
    frame.Show(True)
    app.MainLoop()