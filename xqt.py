# -*- coding: utf-8 -*-
#---------------------
#  XMind2Anki
#---------------------
#  2018-02-22 created
# @Version : 1.1 Beta 
# @Time    : 2018/03/25 14:38
# @Author  : Auxo 
# @File    : xqt.py  
#  
from PyQt4 import QtCore, QtGui
import res_rc
import func
import os
import io
import json
import sys
import codecs
import threading
import filedaemon
from aqt.utils import showInfo
from aqt import mw
from aqt.qt import *
from anki.models import ModelManager


try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

version = u'1.1 Beta'

defaultModelName = u"进阶溯源标记模板-填空"

updateMode = 0 #2为自动更新模式，0为手动更新模式
updateTime = 0 #min
mtime_list = []





class Ui_Dialog(object):
    def __init__(self,parent = None):
        pass

    def setupUi(self, Dialog):
        Dialog.setObjectName(u'Dialog')
        Dialog.setEnabled(True)
        Dialog.resize(399,310)
        Dialog.setWindowTitle(u"XMind2Anki")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(u':/pic/logo.png'), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)

        self.YorN = QtGui.QDialogButtonBox(Dialog)
        self.YorN.setGeometry(QtCore.QRect(240, 280, 151, 21))
        self.YorN.setOrientation(QtCore.Qt.Horizontal)
        self.YorN.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.YorN.setObjectName(u"YorN")

        #页一
        self.config = QtGui.QTabWidget(Dialog)
        self.config.setGeometry(QtCore.QRect(10, 10, 381, 261))
        self.config.setObjectName(u"config")

        self.xmindconfig = QtGui.QWidget()
        self.xmindconfig.setObjectName(u"xmindconfig")

        self.field_func_LView = QtGui.QListView(self.xmindconfig)
        self.field_func_LView.setGeometry(QtCore.QRect(230, 70, 141, 161))
        self.field_func_LView.setObjectName(u"field_func_LView")

        self.xmindPlus_Button = QtGui.QPushButton(u'+',self.xmindconfig)
        self.xmindPlus_Button.setGeometry(QtCore.QRect(170, 41, 20, 20))
        self.xmindPlus_Button.setObjectName(u"xmindPlus_Button")

        self.xmindMinus_Button = QtGui.QPushButton(u'-',self.xmindconfig)
        self.xmindMinus_Button.setGeometry(QtCore.QRect(200, 40, 21, 21))
        self.xmindMinus_Button.setObjectName(u"xmindMinus_Button")

        self.xmindPath_Label = QtGui.QLabel(u'XMind文件路径',self.xmindconfig)
        self.xmindPath_Label.setGeometry(QtCore.QRect(10, 40, 161, 21))
        self.xmindPath_Label.setObjectName(u"xmindPath_Label")

        self.AutoUpdate_ChkBox = QtGui.QCheckBox(u'自动检查',self.xmindconfig)
        self.AutoUpdate_ChkBox.setGeometry(QtCore.QRect(10, 10, 138, 21))
        self.AutoUpdate_ChkBox.setObjectName(u"AutoUpdate_ChkBox")

        self.AutoUpdate2_Label = QtGui.QLabel(u'秒',self.xmindconfig)
        self.AutoUpdate2_Label.setEnabled(False)
        self.AutoUpdate2_Label.setGeometry(QtCore.QRect(130, 10, 31, 21))
        self.AutoUpdate2_Label.setObjectName(u"AutoUpdate2_Label")

        self.AutoUpdateTime_LineEdit = QtGui.QLineEdit(self.xmindconfig)
        self.AutoUpdateTime_LineEdit.setEnabled(False)
        self.AutoUpdateTime_LineEdit.setGeometry(QtCore.QRect(100, 10, 21, 21))
        self.AutoUpdateTime_LineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.AutoUpdateTime_LineEdit.setObjectName(u"AutoUpdateTime_LineEdit")

        self.Update_Button = QtGui.QPushButton(u"增量",self.xmindconfig)
        self.Update_Button.setGeometry(QtCore.QRect(190, 10, 30, 21))
        self.Update_Button.setObjectName(u"Update_Button")

        self.fullUpdate_Button = QtGui.QPushButton(u"全量",self.xmindconfig)
        self.fullUpdate_Button.setGeometry(QtCore.QRect(160, 10, 30, 21))
        self.fullUpdate_Button.setObjectName(u"FullUpdate_Button")

        self.AutoUpdate1_Label = QtGui.QLabel(u"每",self.xmindconfig)
        self.AutoUpdate1_Label.setEnabled(False)
        self.AutoUpdate1_Label.setGeometry(QtCore.QRect(80, 10, 21, 21))
        self.AutoUpdate1_Label.setObjectName(u"AutoUpdate1_Label")

        self.model_ComboBox = QtGui.QComboBox(self.xmindconfig)
        self.model_ComboBox.setGeometry(QtCore.QRect(60, 160, 161, 21))
        self.model_ComboBox.setObjectName(u"model_ComboBox")

        self.model_Label = QtGui.QLabel(u"默认模板",self.xmindconfig)
        self.model_Label.setGeometry(QtCore.QRect(10, 160, 51, 21))
        self.model_Label.setObjectName(u"model_Label")

        self.field_Label = QtGui.QLabel(u"字段",self.xmindconfig)
        self.field_Label.setGeometry(QtCore.QRect(230, 10, 51, 21))
        self.field_Label.setObjectName(u"field_Label")

        self.field_ComboBox = QtGui.QComboBox(self.xmindconfig)
        self.field_ComboBox.setGeometry(QtCore.QRect(260, 10, 81, 21))
        self.field_ComboBox.setObjectName(u"field_ComboBox")

        self.function_Label = QtGui.QLabel(u"功能",self.xmindconfig)
        self.function_Label.setGeometry(QtCore.QRect(230, 40, 51, 21))
        self.function_Label.setObjectName(u"function_Label")

        self.function_ComboBox = QtGui.QComboBox(self.xmindconfig)
        self.function_ComboBox.setGeometry(QtCore.QRect(260, 40, 81, 21))
        self.function_ComboBox.setObjectName(u"function_ComboBox")

        self.function_ComboBox.addItem(u"挖空问答") #0
        self.function_ComboBox.addItem(u"路径") #1
        self.function_ComboBox.addItem(u"相关_答") #2
        self.function_ComboBox.addItem(u"相关_问") #3
        self.function_ComboBox.addItem(u"思维导图") #4
        self.function_ComboBox.addItem(u"ID") #5
        self.function_ComboBox.addItem(u"时间戳") #6
        self.function_ComboBox.addItem(u"孙节点内容") #7
        self.function_ComboBox.addItem(u"外部链接") #8
        self.function_ComboBox.addItem(u"图片") #9
        self.function_ComboBox.addItem(u"概要") #10



        self.xmindPath_LWidget = QtGui.QListWidget(self.xmindconfig)
        self.xmindPath_LWidget.setGeometry(QtCore.QRect(10, 70, 211, 81))
        self.xmindPath_LWidget.setObjectName(u"xmindPath_LWidget")


        self.functionPlus_Button = QtGui.QPushButton(u'+',self.xmindconfig)
        self.functionPlus_Button.setGeometry(QtCore.QRect(350, 10, 21, 21))
        self.functionPlus_Button.setObjectName(u"functionPlus_Button")
        self.functionMinus_Button = QtGui.QPushButton(u'-',self.xmindconfig)
        self.functionMinus_Button.setGeometry(QtCore.QRect(350, 40, 21, 21))
        self.functionMinus_Button.setObjectName(u"functionMinus_Button")

        self.customModel_ChkBox = QtGui.QCheckBox(u"允许使用XMind内自定义模板",self.xmindconfig)
        self.customModel_ChkBox.setEnabled(False)
        self.customModel_ChkBox.setGeometry(QtCore.QRect(10, 190, 171, 16))
        self.customModel_ChkBox.setObjectName(u"customModel_ChkBox")

        self.EchoLength1_Label = QtGui.QLabel(u"返回值单行长度",self.xmindconfig)
        self.EchoLength1_Label.setGeometry(QtCore.QRect(10, 210, 91, 21))
        self.EchoLength1_Label.setObjectName(u"EchoLength1_Label")

        self.EchoLength_LineEdit = QtGui.QLineEdit(self.xmindconfig)
        self.EchoLength_LineEdit.setGeometry(QtCore.QRect(100, 210, 31, 21))
        self.EchoLength_LineEdit.setObjectName(u"EchoLength_LineEdit")

        self.EchoLength2_Label = QtGui.QLabel(u'字符',self.xmindconfig)
        self.EchoLength2_Label.setGeometry(QtCore.QRect(140, 210, 31, 21))
        self.EchoLength2_Label.setObjectName(u"EchoLength2_Label")

        self.config.addTab(self.xmindconfig, u"XMind转换配置")
        self.markconfig = QtGui.QWidget()
        self.markconfig.setObjectName(u"markconfig")


        ##
        ##    页二
        ############################

        self.groupBox = QtGui.QGroupBox(u"应用于节点",self.markconfig)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 101, 161))
        self.groupBox.setObjectName(u"groupBox")

        self.label_2 = QtGui.QLabel(u'-起始',self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(30, 100, 31, 21))
        self.label_2.setObjectName(u"label_2")

        self.label_3 = QtGui.QLabel(u"-终止",self.groupBox)
        self.label_3.setGeometry(QtCore.QRect(30, 130, 31, 21))
        self.label_3.setObjectName(u"label_3")

        self.endClozeMark_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.endClozeMark_lineEdit.setGeometry(QtCore.QRect(70, 130, 21, 21))
        self.endClozeMark_lineEdit.setObjectName(u"endClozeMark_lineEdit")

        self.startClozeMark_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.startClozeMark_lineEdit.setGeometry(QtCore.QRect(70, 100, 21, 21))
        self.startClozeMark_lineEdit.setObjectName(u"startClozeMark_lineEdit")

        self.label = QtGui.QLabel(u"挖空标记",self.groupBox)
        self.label.setGeometry(QtCore.QRect(10, 80, 51, 21))
        self.label.setObjectName(u"label")

        self.label_5 = QtGui.QLabel(u"多空标记",self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(10, 50, 51, 21))
        self.label_5.setObjectName(u"label_5")

        self.label_4 = QtGui.QLabel(u"转换标记",self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(10, 20, 108, 21))
        self.label_4.setObjectName(u"label_4")

        self.TransMark_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.TransMark_lineEdit.setGeometry(QtCore.QRect(70, 20, 21, 21))
        self.TransMark_lineEdit.setObjectName(u"TransMark_lineEdit")

        self.MultiMark_lineEdit = QtGui.QLineEdit(self.groupBox)
        self.MultiMark_lineEdit.setGeometry(QtCore.QRect(70, 50, 21, 21))
        self.MultiMark_lineEdit.setObjectName(u"MultiMark_lineEdit")

        self.groupBox_2 = QtGui.QGroupBox(u"应用于子节点",self.markconfig)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 180, 101, 51))
        self.groupBox_2.setObjectName(u"groupBox_2")

        self.ExcludeMark_lineEdit = QtGui.QLineEdit(self.groupBox_2)
        self.ExcludeMark_lineEdit.setGeometry(QtCore.QRect(70, 20, 21, 21))
        self.ExcludeMark_lineEdit.setObjectName(u"ExcludeMark_lineEdit")

        self.label_6 = QtGui.QLabel(u"排除标记",self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(10, 20, 51, 21))
        self.label_6.setObjectName(u"label_6")

        self.groupBox_3 = QtGui.QGroupBox(u"应用于根节点",self.markconfig)
        self.groupBox_3.setGeometry(QtCore.QRect(120, 10, 111, 71))
        self.groupBox_3.setObjectName(u"groupBox_3")

        self.SubMark_lineEdit = QtGui.QLineEdit(self.groupBox_3)
        self.SubMark_lineEdit.setGeometry(QtCore.QRect(80, 20, 21, 21))
        self.SubMark_lineEdit.setObjectName(u"SubMark_lineEdit")

        self.label_7 = QtGui.QLabel(u"子Deck标记",self.groupBox_3)
        self.label_7.setGeometry(QtCore.QRect(10, 20, 61, 21))
        self.label_7.setObjectName(u"label_7")

        self.label_8 = QtGui.QLabel(u"Deck名源于根节点",self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(10, 40, 101, 24))
        self.label_8.setObjectName(u"label_8")

        self.groupBox_4 = QtGui.QGroupBox(u"应用于子节点内容",self.markconfig)
        self.groupBox_4.setGeometry(QtCore.QRect(120, 90, 111, 81))
        self.groupBox_4.setObjectName(u"groupBox_4")

        self.label_13 = QtGui.QLabel(u"子项分隔符",self.groupBox_4)
        self.label_13.setGeometry(QtCore.QRect(10, 20, 61, 21))
        self.label_13.setObjectName(u"label_13")

        self.ChildsMark_lineEdit = QtGui.QLineEdit(self.groupBox_4)
        self.ChildsMark_lineEdit.setGeometry(QtCore.QRect(80, 20, 21, 20))
        self.ChildsMark_lineEdit.setObjectName(u"ChildsMark_lineEdit")

        self.label_14 = QtGui.QLabel(u"Q&A分隔符",self.groupBox_4)
        self.label_14.setGeometry(QtCore.QRect(10, 50, 61, 21))
        self.label_14.setObjectName(u"label_14")

        self.QAMark_lineEdit = QtGui.QLineEdit(self.groupBox_4)
        self.QAMark_lineEdit.setGeometry(QtCore.QRect(80, 50, 21, 21))
        self.QAMark_lineEdit.setObjectName(u"QAMark_lineEdit")

        self.groupBox_5 = QtGui.QGroupBox(u"应用于孙节点",self.markconfig)
        self.groupBox_5.setGeometry(QtCore.QRect(120, 180, 111, 51))
        self.groupBox_5.setObjectName(u"groupBox_5")

        self.label_15 = QtGui.QLabel(u"孙项等级符",self.groupBox_5)
        self.label_15.setGeometry(QtCore.QRect(10, 20, 61, 21))
        self.label_15.setObjectName(u"label_15")

        self.LevelMark_lineEdit = QtGui.QLineEdit(self.groupBox_5)
        self.LevelMark_lineEdit.setGeometry(QtCore.QRect(80, 20, 21, 21))
        self.LevelMark_lineEdit.setObjectName(u"LevelMark_lineEdit")

        self.groupBox_6 = QtGui.QGroupBox(u"其余符号配置",self.markconfig)
        self.groupBox_6.setGeometry(QtCore.QRect(240, 10, 131, 81))
        self.groupBox_6.setObjectName(u"groupBox_6")

        self.SummaryCMark_lineEdit = QtGui.QLineEdit(self.groupBox_6)
        self.SummaryCMark_lineEdit.setGeometry(QtCore.QRect(100, 20, 21, 21))
        self.SummaryCMark_lineEdit.setObjectName(u"SummaryCMark_lineEdit")

        self.label_17 = QtGui.QLabel(self.groupBox_6)
        self.label_17.setGeometry(QtCore.QRect(20, 80, 121, 31))
        self.label_17.setText(u"")
        self.label_17.setObjectName(u"label_17")

        self.label_18 = QtGui.QLabel(u"[概要]分隔符",self.groupBox_6)
        self.label_18.setGeometry(QtCore.QRect(20, 20, 81, 21))
        self.label_18.setObjectName(u"label_18")

        self.label_19 = QtGui.QLabel(u"[概要]总结符",self.groupBox_6)
        self.label_19.setGeometry(QtCore.QRect(20, 50, 71, 21))
        self.label_19.setObjectName(u"label_19")

        self.SummaryEqMark_lineEdit = QtGui.QLineEdit(self.groupBox_6)
        self.SummaryEqMark_lineEdit.setGeometry(QtCore.QRect(100, 50, 21, 21))
        self.SummaryEqMark_lineEdit.setObjectName(u"SummaryEqMark_lineEdit")

        self.label_20 = QtGui.QLabel(u"Version",self.markconfig)
        self.label_20.setGeometry(QtCore.QRect(250, 210, 51, 21))
        font = QtGui.QFont()
        font.setFamily(u"Calibri")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_20.setFont(font)
        self.label_20.setStyleSheet(u"")
        self.label_20.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_20.setObjectName(u"label_20")

        self.version_Label = QtGui.QLabel(version,self.markconfig)
        self.version_Label.setGeometry(QtCore.QRect(300, 210, 51, 21))
        font = QtGui.QFont()
        font.setFamily(u"Calibri")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.version_Label.setFont(font)
        self.version_Label.setStyleSheet(u"")
        self.version_Label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.version_Label.setObjectName(u"version_Label")

        self.Logo_Label = QtGui.QLabel(self.markconfig)
        self.Logo_Label.setGeometry(QtCore.QRect(250,100,111,111))
        self.Logo_Label.setText(u"")
        self.Logo_Label.setPixmap(QtGui.QPixmap(u":/pic/logo.png"))
        self.Logo_Label.setScaledContents(True)
        self.Logo_Label.setObjectName(u"Logo_Label")
        
        self.config.addTab(self.markconfig, u"标记定义")

        self.progressBar = QtGui.QProgressBar(Dialog)
        func.pr = []
        func.pr.append(self.progressBar)
        self.progressBar.setGeometry(QtCore.QRect(10, 280, 181, 21))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(u"progressBar")
        
        self.progressLabel = QtGui.QLabel(u"0/0:0/0",Dialog)
        func.pr.append(self.progressLabel)
        self.progressLabel.setGeometry(QtCore.QRect(188, 280, 50, 21))
        self.progressLabel.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.progressLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.progressLabel.setObjectName(u"progressLabel")


        self.config.setCurrentIndex(0)

        #Signal2Slot
        QtCore.QObject.connect(self.YorN, QtCore.SIGNAL(u"accepted()"), self.Dialog_accept)
        QtCore.QObject.connect(self.YorN, QtCore.SIGNAL(u"accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.YorN, QtCore.SIGNAL(u"rejected()"), Dialog.reject)
        QtCore.QObject.connect(self.AutoUpdate_ChkBox, QtCore.SIGNAL(u"toggled(bool)"), self.AutoUpdateTime_LineEdit.setEnabled)
        QtCore.QObject.connect(self.AutoUpdate_ChkBox, QtCore.SIGNAL(u"toggled(bool)"), self.AutoUpdate1_Label.setEnabled)
        QtCore.QObject.connect(self.AutoUpdate_ChkBox, QtCore.SIGNAL(u"toggled(bool)"), self.AutoUpdate2_Label.setEnabled)
        QtCore.QObject.connect(self.xmindMinus_Button, QtCore.SIGNAL(u"clicked()"), self.xmind_removeFile)
        QtCore.QObject.connect(self.xmindPlus_Button, QtCore.SIGNAL(u"clicked()"), self.xmind_openFile)
        QtCore.QObject.connect(self.Update_Button, QtCore.SIGNAL(u"clicked()"), self.update)
        QtCore.QObject.connect(self.fullUpdate_Button, QtCore.SIGNAL(u"clicked()"), self.fullUpdate)
        QtCore.QObject.connect(self.model_ComboBox, QtCore.SIGNAL(u"currentIndexChanged(int)"), self.selectModelName)

        self.Dialog_init()

    #
    #     功能区
    #############################


    ##辅助功能

    def QStr2PyStr(self, qStr):
        # # QString，如果内容是中文，则直接使用会有问题，要转换成 python string
        return unicode(qStr.toUtf8(), 'utf-8', 'ignore')

    #
    # # 更新
    ###################
    def update(self):
        '''
        用ini传递参数,先保存,再调用func读取内容
        '''
        self.Dialog_accept()#保存json
        #调用func
        func.init()
        return

    def fullUpdate(self):
        '''
        用ini传递参数,先保存,再调用func读取内容
        '''
        self.Dialog_accept()#保存json
        #调用func
        func.init(FullMode=True)
        return

    def mtimeChecker(self):
        return



    #
    # # xmind文件选择
    ###################

    def xmind_openFile(self):  
        s=QtGui.QFileDialog.getOpenFileName(None,"Open XMind File","C:\\","XMind files(*.xmind)")
        count = self.xmindPath_LWidget.count()
        items = [self.xmindPath_LWidget.item(i).text() for i in range(0,count) if count != 0]
        
        if str(s) not in items:
            self.xmindPath_LWidget.addItem(unicode(s))
            mtime = os.stat(unicode(s)).st_mtime
            mtime_list.append(mtime)
        return

    def xmind_removeFile(self):
        item_deleted = self.xmindPath_LWidget.takeItem(self.xmindPath_LWidget.currentRow()) 
        #将读取的值设置为None  
        item_deleted = None 
        return

    #
    # # 模板选择
    ###################

    def loadModelNames(self):
        allNames = mw.col.models.allNames()
        modelName = u''
        select = -1
        json_exist = os.path.exists(self.json_Path)
        try:
            mid = self.data[u"Util"][u"mid"]
        except:
            mid = 0

        if json_exist and mid:
            json_modelName = mw.col.models.get(mid)['name']
            if json_modelName:
                modelName = json_modelName
            else:
                modelName = defaultModelName
        else:
            modelName = defaultModelName
        #添加所有模板名
        for i in range(len(allNames)-1):
            self.model_ComboBox.addItem(allNames[i])
            if allNames[i] == modelName:
                select = i

        self.model_ComboBox.setCurrentIndex(select)
        return

    def selectModelName(self):
        modelName = self.model_ComboBox.currentText()
        mid = mw.col.models.byName(modelName)['id']
        m = mw.col.models.get(mid)
        fieldNames = [f['name'] for f in m['flds']]
        self.field_ComboBox.clear()
        for i in range(len(fieldNames)-1):
            self.field_ComboBox.addItem(fieldNames[i])
        return
                
 



    def Dialog_init(self):
        '''
        读入模板名称
        读入配置文件
        '''
        global mtime_list
        AnkiRoot_absPath = mw.col.path.replace(u'collection.anki2','')
        self.json_Path = AnkiRoot_absPath+ u'\\x2a.json'
        self.loadModelNames()#读入模板名称

        json_exist = os.path.exists(self.json_Path)

        if json_exist:
            #创建配置文件操作对象
            self.data={} #存放读取的数据
            with io.open(self.json_Path,'r',encoding='utf-8') as json_file:
                self.data=json.load(json_file)

            #读取用户配置信息
            self.AutoUpdateYN = self.data[u"Util"][u"AutoUpdateYN"]
            updateMode = self.AutoUpdateYN
            self.AutoUpdateTime = self.data[u"Util"][u"AutoUpdateTime"]
            updateTime = self.AutoUpdateTime
            EchoLength = self.data[u"Util"][u"EchoLength"]
            self.Path = self.data[u"Util"][u"Path"]
            mtime_str = self.data[u"Util"][u"mtime"].split(u'|')
            if mtime_str[0]:
                mtime_list = [float(x) for x in mtime_str]
            endClozeMark = self.data[u"Mark"][u"endClozeMark"]
            startClozeMark = self.data[u"Mark"][u"startClozeMark"]
            TransMark = self.data[u"Mark"][u"TransMark"]
            MultiMark = self.data[u"Mark"][u"MultiMark"]
            ExcludeMark = self.data[u"Mark"][u"ExcludeMark"]
            SubMark = self.data[u"Mark"][u"SubMark"]
            ChildsMark = self.data[u"Mark"][u"ChildsMark"]
            QAMark = self.data[u"Mark"][u"QAMark"]
            LevelMark = self.data[u"Mark"][u"LevelMark"]
            SummaryCMark = self.data[u"Mark"][u"SummaryCMark"]
            SummaryEqMark = self.data[u"Mark"][u"SummaryEqMark"]


            #读入参数
            self.AutoUpdate_ChkBox.setCheckState(self.AutoUpdateYN)
            self.AutoUpdateTime_LineEdit.setText(str(self.AutoUpdateTime))
            self.EchoLength_LineEdit.setText(str(EchoLength))
            self.endClozeMark_lineEdit.setText(endClozeMark)
            self.startClozeMark_lineEdit.setText(startClozeMark)
            self.TransMark_lineEdit.setText(TransMark)
            self.MultiMark_lineEdit.setText(MultiMark)
            self.ExcludeMark_lineEdit.setText(ExcludeMark)
            self.SubMark_lineEdit.setText(SubMark)
            self.ChildsMark_lineEdit.setText(ChildsMark)
            self.QAMark_lineEdit.setText(QAMark)
            self.LevelMark_lineEdit.setText(LevelMark)
            self.SummaryCMark_lineEdit.setText(SummaryCMark)
            self.SummaryEqMark_lineEdit.setText(SummaryEqMark)
            if self.Path:
                self.xmindPath_LWidget.addItems(self.Path.split(u'|'))
            return
        else:
            self.AutoUpdateTime_LineEdit.setText(u"20")
            self.EchoLength_LineEdit.setText(u"25")
            self.endClozeMark_lineEdit.setText(u"]")
            self.startClozeMark_lineEdit.setText(u"[")
            self.TransMark_lineEdit.setText(u"#")
            self.MultiMark_lineEdit.setText(u"*")
            self.ExcludeMark_lineEdit.setText(u"~")
            self.SubMark_lineEdit.setText(u"-")
            self.ChildsMark_lineEdit.setText(u"、")
            self.QAMark_lineEdit.setText(u":")
            self.LevelMark_lineEdit.setText(u"\\t")
            self.SummaryCMark_lineEdit.setText(u"+")
            self.SummaryEqMark_lineEdit.setText(u"→")
            return


    def Dialog_accept(self):
        '''
        写入配置文件
        '''
        #获取参数
        AutoUpdateYN = int(self.AutoUpdate_ChkBox.checkState())
        updateMode = AutoUpdateYN
        AutoUpdateTime = int(self.AutoUpdateTime_LineEdit.text())
        UpdateTime = AutoUpdateTime
        EchoLength = int(self.EchoLength_LineEdit.text())
        endClozeMark = self.endClozeMark_lineEdit.text()
        startClozeMark = self.startClozeMark_lineEdit.text()
        TransMark = self.TransMark_lineEdit.text()
        MultiMark = self.MultiMark_lineEdit.text()
        ExcludeMark = self.ExcludeMark_lineEdit.text()
        SubMark = self.SubMark_lineEdit.text()
        ChildsMark = self.ChildsMark_lineEdit.text()
        QAMark = self.QAMark_lineEdit.text()
        LevelMark = self.LevelMark_lineEdit.text()
        SummaryCMark = self.SummaryCMark_lineEdit.text()
        SummaryEqMark = self.SummaryEqMark_lineEdit.text()
        #-----path------
        count = self.xmindPath_LWidget.count()
        items = [str(self.xmindPath_LWidget.item(i).text()) for i in range(0,count) if count != 0]
        strPath = u'|'.join(items)
        #-----mtime-----
        str_mtime_list = [str(x) for x in mtime_list]
        strmtime = u'|'.join(str_mtime_list)
        #model
        modelName = self.model_ComboBox.currentText()
        mid = mw.col.models.byName(modelName)['id']

        #创建配置文件操作对象
        ex_data = {} 

        #将信息写入配置文件
        ex_data[u"Util"] = {}
        ex_data[u"Mark"] = {}
        
        ex_data[u"Util"]['AutoUpdateTime'] = AutoUpdateTime
        ex_data[u"Util"]['AutoUpdateYN'] = AutoUpdateYN
        ex_data[u"Util"]['EchoLength'] = EchoLength
        if items:
            ex_data[u"Util"]['Path'] = strPath
            ex_data[u"Util"]['mtime'] = strmtime
        else:
            ex_data[u"Util"]['Path'] = ''
            ex_data[u"Util"]['mtime'] = ''
        ex_data[u"Util"]['mid'] = mid
        ex_data[u"Mark"]['endClozeMark'] = endClozeMark
        ex_data[u"Mark"]['startClozeMark'] = startClozeMark
        ex_data[u"Mark"]['TransMark'] = TransMark
        ex_data[u"Mark"]['MultiMark'] = MultiMark
        ex_data[u"Mark"]['ExcludeMark'] = ExcludeMark
        ex_data[u"Mark"]['SubMark'] = SubMark
        ex_data[u"Mark"]['ChildsMark'] = ChildsMark
        ex_data[u"Mark"]['QAMark'] = QAMark
        ex_data[u"Mark"]['LevelMark'] = LevelMark
        ex_data[u"Mark"]['SummaryCMark'] = SummaryCMark
        ex_data[u"Mark"]['SummaryEqMark'] = SummaryEqMark

        formated = json.dumps(ex_data, sort_keys=True, indent=4, ensure_ascii=False)
        with codecs.open(self.json_Path,'w','utf-8') as w:
            w.write(formated)
        return


class MainWindow(QtGui.QDialog): 

    def __init__(self, mw):

        QtGui.QWidget.__init__(self,parent=mw)
        self.ui=Ui_Dialog()# Ui_Dialog为.ui产生.py文件中窗体类名，经测试类名以Ui_为前缀，加上UI窗体对象名（此处为Dialog）
        self.ui.setupUi(self)


class windowConstructor(object):
    
    def __init__(self,mw):
        """Call settings dialog"""
        self.dialog = MainWindow(mw)
        self.dialog.exec_()

def updateButton():
    func.init()
    return

options_action = QAction(u"XMind2Anki配置", mw)
options_action.triggered.connect(lambda _, o=mw: windowConstructor(o))
mw.form.menuTools.addAction(options_action)
