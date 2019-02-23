# -*- coding: utf-8 -*-
#---------------------
#  XMind2Anki
#---------------------
#  2018-03-26 created
# @Version : 1.1 Beta 
# @Time    : 2018/03/26 16:42
# @Author  : Auxo 
# @File    : filedaemon.py  
#  
import os
import io
from aqt.utils import showInfo
from aqt import mw
from anki.hooks import addHook
import func
import json
import codecs
Path = []
updateTime = 20


class AutoUpdate:
    def __init__(self):
        self.timer = None
        self.currentUser = None
        self.AnkiRoot_absPath = None
        self.json_Path = None
        self.Path = None
        self.old_mtimes = None
        self.new_mtimes = []

        self.initTimer()


    def initTimer(self):
        if self.timer is not None:
            self.timer.stop()
        self.timer = mw.progress.timer(5000, self.checkEnv, True)
        return

    def checkEnv(self):
        allDone = False
        if 'Program Files' not in os.getcwd():  
            self.AnkiRoot_absPath = os.getcwd().replace(u'collection.media','')
            self.json_Path = self.AnkiRoot_absPath+ u'\\x2a.json'
            self.currentUser = self.getUser()
            json_exist = os.path.exists(self.json_Path)
            #showInfo('checkEnv')
            if json_exist:
                #创建配置文件操作对象
                self.data={} #存放读取的数据
                with io.open(self.json_Path,'r',encoding='utf-8') as json_file:
                    self.data=json.load(json_file)

                self.AutoUpdateYN = self.data[u"Util"][u"AutoUpdateYN"]
                self.AutoUpdateTime = self.data[u"Util"][u"AutoUpdateTime"]
                allDone = True
            else:return #记得在func新建json的函数里激活这个时钟
        
        #完成全部准备事项后进入循环监控文件阶段
        if allDone:
            self.startTimer(self.AutoUpdateTime)
        return


    def startTimer(self, seconds):
        """Start the timer/reset the timer if the updateTime changed"""
        if self.timer is not None:
            self.timer.stop()
        self.timer = mw.progress.timer(1000*seconds, self.UpdateController, True)

    def UpdateController(self):
        """如果满足下面所有条件则开始更新"""
        #判断是否为当前用户配置
        if self.currentUser != self.getUser():
            #不是，则返回初始检查环境步骤
            self.initTimer()
        
        #上面的都满足了进入更新判断
        self.Update()
        return


    def Update(self):
        if self.AutoUpdateYN == 2:#如果为自动模式
            showInfo('update mode!')
            #读取记录的文件修改时间
            self.readJsonmtime()
            self.CHANGE = False
            #比对文件修改时间
            self.new_mtimes = []
            for i in range(0,len(self.Path)):
                new_mtime = os.stat(self.Path[i]).st_mtime
                self.new_mtimes.append(new_mtime)
                if new_mtime != self.old_mtimes[i]:
                    showInfo("something wrong!"+str(type(new_mtime))+str(type(self.old_mtimes[i])))
                    self.CHANGE = True
            if self.CHANGE == True:
                #如果有文件变动
                showInfo('shit')
                func.init(AutoMode=True)
                self.updateJsonmtime()
                self.old_mtimes = self.new_mtimes
                self.CHANGE = False

        return

    def getUser(self):
        return os.getcwd().split('\\')[-2]


    def readJsonmtime(self):
        
        json_exist = os.path.exists(self.json_Path)
        if json_exist:
            #创建配置文件操作对象
            self.data={} #存放读取的数据
            with io.open(self.json_Path,'r',encoding='utf-8') as json_file:
                self.data=json.load(json_file)
            self.Path = self.data[u"Util"][u"Path"].split(u'|')
            mtime_str = self.data[u"Util"][u"mtime"].split(u'|')
            showInfo (self.data[u"Util"][u"mtime"])
            if mtime_str[0]:
                self.old_mtimes = [float(x) for x in mtime_str]
        return

    def updateJsonmtime(self):
        json_exist = os.path.exists(self.json_Path)

        if json_exist:
            str_new_mtimes = [str(x) for x in self.new_mtimes]
            join_new_mtimes = u"|".join(str_new_mtimes)
            self.data[u"Util"][u"mtime"] = join_new_mtimes
            showInfo("updatedata")
            formated = json.dumps(self.data, sort_keys=True, indent=4, ensure_ascii=False)
            with codecs.open(self.json_Path,'w','utf-8') as w:
                w.write(formated)
            return

AutoUpdate()
