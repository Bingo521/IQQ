class User(object):
    def __init__(self,username="",count="",isOnLine=0):
        self.username=username
        self.count=count
        self.isOnLine=isOnLine
        self.ex=dict()

class Inform(object):
    def __init__(self,type,data):
        self.type=type
        self.data=data
class MyFile(object):
    def __init__(self,filename,file):
        self.filename=filename
        self.file=file
class MyPotocol(object):
    def __init__(self, Pno=0, Pdata=0):
        self.pno = Pno
        self.data = Pdata

    def getPno(self):
        return self.pno

    def setPno(self, Pno):
        self.pno = Pno

    def getPdata(self):
        return self.data

    def setPdata(self, Pdata):
        self.data = Pdata
class POTOCOL(object):
    #com
    IP          =   "127.0.0.1"
    PORT        =   7075
    #sys
    SADDFL      =   0
    SONLINE     =   1
    SOFFLINE    =   2
    SFJOIN      =   3
    SMESSBOX    =   4
    SONLINEED   =   5
    SSUCCESS    =   6
    SALIVE      =   7
    SRSUCCESS   =   8
    SADDF       =   9
    SCHSTAUS    =   10
    SADDUSER    =   11
    SINITSELF   =   12
    SSENDFILE   =   13
    SINFOFILE   =   14
    #user
    UOFFLINE    =   1000
    ULOGIN      =   1001
    UADDF       =   1002
    USENDWORD   =   1003
    UREGITSER   =   1004
    UCOUNTERR   =   1005
    UOK         =   1006
    UDELETEINFO =   1007
    UMESS       =   1008
    UDELETEID   =   1009
    UREFUSE     =   1010
    UDELETEF    =   1011
    USENDFILE   =   1012
    UGETFILE    =   1013
    #comm
    UAGREE      =   2007
    #string

    DES         =       "des"
    RES         =       "res"
    COUNT       =       "count"
    PASSWORD    =       "password"
    USERNAME    =       "username"
    STAUS       =       "staus"
    MESS        =       "mess"
    DATE        =       "date"
    USER        =       "user"
    ID          =       "id"
    STOREPATH   =       "storepath.path"
    FILE        =       "file"
    FILENAME    =       "filename"
    MESSNUM     =       "messnum"
    PROCESS     =       "process"
    INFOID      =       "infoid"
    FILELEN     =       "filelen"
    SPEED       =       "speed"
    #menu
    FRIENDLIST  =   0
    MESSLIST    =   1
    ADDLIST     =   2
    INFOLIST    =   3
    CONTROL     =   4
    #db
    DBNAME  ="IQQ.db"
    #count base
    BASE    =   123456
    #inform
    INFOADD     =   0
    INFO        =   1
    INFOFILE    =   2
    INFOFILEOK  =   3
    INFORECV    =   4
    INFORECVOK  =   5
    INFOSEND    =   6
    INFOSENDOK    =   7
    INFOTIP     =   "tip"
    FMENU       =   100
    # ico path
    DEFAULTICO  =   "img/OnLine.jpg"
    INFOICO = [
        "img/infoadd.jpg",
        "img/info.jpg",
        "img/infofile.jpg",
        "img/infofileok.jpg",
        "img/inforecv.jpg",
        "img/inforecvok.jpg",
        "img/infosend.jpg",
        "img/infosendok.jpg"
    ]
    OFFONICO    =   [
        "img/OffLine.jpg",
        "img/OnLine.jpg"
    ]
    #messtype
    MINFO       =   0
    MMESS       =   1
    MFILE       =   2
    #Log
    LOGDEBUG       =   "DEBUG"
    LOGINFO        =   "INFO"
    LOGERROR       =   "ERROR"
    LOGNAME        =   "IQQ"
    DEBUG          =   1
    #path dir
    PATHFILE           =    "file"

    def __init__(self):
        pass