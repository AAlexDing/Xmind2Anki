# -*- coding: utf-8 -*-
#---------------------
#  XMind2Anki
#---------------------
#  2018-01-04 created
# @Version : 1.1 Beta 
# @Time    : 2018/09/05 19:40
# @Author  : Auxo 
# @File    : func.py  
#  
from __future__ import with_statement
import xmind
import os
import io
import zipfile
import string
import anki
import aqt
import json
import codecs
import random
import time
from difflib import SequenceMatcher as sm
from aqt import mw
from xmind.core import Element
from xmind.core.topic import TopicElement
from xmind.core.relationship import RelationshipElement
from xmind.core import Node
from xmind.core import const
from xmind import utils
from xml.dom import minidom as DOM
from aqt.utils import showInfo,showText
#from xqt import windowConstructor.dialog.ui as xui
"""
默认ANKI中的deck名称源于每个sheet的根节点title
修改模块时检查一下调用模块的相互关系

"""

#
#Anki内容相关
#



######配置区域############################
#QA相似度
#文字相似率
similarityAimRatio = 0.5 
#路径相似率
dir_similarityAimRatio = 0.9

QMinLength = 5 #问题的最小长度，小于此则增加父项Title
QMaxLength = 12 #问题的最大长度，大于此则换行
AMaxLength = 12 #答案单项最大长度，大于此则换行

IDSeparator = "," #ID分隔符
IMGSeparator = ";" #ID和IMG的分隔符

MANUAL_FLD_NAMES = [u'q_addition',u'notes',u'mark']

MarkerID_num = {
    'priority-1': 1,
    'priority-2': 2,
    'priority-3': 3
    }


#CONST
TOPIC_SUMMARY = "summary"

TAG_LABELS="labels"
TAG_LABEL="label"
TAG_IMG = "xhtml:img"
ATTR_IMGSRC = "xhtml:src"
STR_IMG = "xap:"

TAG_LABELS = "labels"
TAG_LABEL = "label"

TAG_SUMMARIES = "summaries"
TAG_SUMMARY = "summary"

TIMESTAMP_MAXDEPTH = 3

fld_ID_name = u'ID'
fld_TIMESTAMP_name = u'TIMESTAMP'
fld_QA_name = u'QA'

LevelMark = u'　　'#孙项等级符号
LevelMarkEnd = u'　└'#孙项等级符号结束


MULTIMEDIA_TEXT = u'图'
pr = []#参数传递者

globalPrinter = u''



class init(object):
    def __init__(self,AutoMode=False,FullMode=False):
        global globalPrinter,MANUAL_FLD_NAMES,func_AutoMode,AutoUpdateYN,AnkiRoot_absPath,AnkiMedia_relPath,AnkiAddons_absPath,json_Path,echoChrLength,PATHS,mid,end_ClozeMark,start_ClozeMark,TransMark,MultiMark,ExcludeMark,SubMark,ChildsSeparator,QASeparator,LevelMark,LevelMarkEnd,SummaryConnector,SummaryEqualMark,modelName,pBar,pLabel
        AnkiRoot_absPath = mw.col.path.replace(u'collection.anki2','')
        AnkiMedia_relPath = u'collection.media/'
        func_AutoMode = AutoMode
        self.FullMode = FullMode

        json_Path = AnkiRoot_absPath+ u'\\x2a.json'
        exist = os.path.exists(json_Path)
        
        if not func_AutoMode:
            pBar = pr[0]
            pLabel = pr[1]

        if exist:
            #创建配置文件操作对象
            data={} #存放读取的数据
            with io.open(json_Path,'r',encoding='utf-8') as json_file:
                data=json.load(json_file)
            #读取用户配置信息
            #目标文件
            echoChrLength = data[u"Util"][u"EchoLength"]
            AutoUpdateYN = data[u"Util"][u"AutoUpdateYN"]
            PATHS = data[u"Util"][u"Path"].split(u'|')
            mid = data[u"Util"][u"mid"]
            end_ClozeMark = data[u"Mark"][u"endClozeMark"]#挖空标记-末
            start_ClozeMark = data[u"Mark"][u"startClozeMark"]#挖空标记-始
            TransMark = data[u"Mark"][u"TransMark"]#转换标记
            MultiMark = data[u"Mark"][u"MultiMark"]#多空标记
            ExcludeMark = data[u"Mark"][u"ExcludeMark"]#排除标记(仅用于子项)
            SubMark = data[u"Mark"][u"SubMark"]#Anki子Deck标记(将被转换为::)
            ChildsSeparator = data[u"Mark"][u"ChildsMark"]#子项文本分隔符 (程序完成后替换为顿号)
            QASeparator = data[u"Mark"][u"QAMark"]#QA分隔符
            SummaryConnector = data[u"Mark"][u"SummaryCMark"]
            SummaryEqualMark = data[u"Mark"][u"SummaryEqMark"]
            modelName = mw.col.models.get(mid)['name']

            #启动处理
            if PATHS[0]:
                return self.launcher()
            else:
                showInfo(u'无XMind文件选中！')
        else:
            showInfo(u"读取json失败,请检查路径可用性")

    def launcher(self):
        global globalPrinter
        pathcounter = 0
        pathnum = len(PATHS)
        for path in PATHS:
            global ALL_IDS_WORKBOOK,ALL_TOPICS_WORKBOOK,init_Sheet,fz
            pathcounter += 1
            sheetcounter = 0
            workbook = xmind.load(path)
            sheets = workbook.getSheets()
            targetSheets = list(filter(ObjectTitleFilter(TransMark),sheets))
            sheetnum = len(targetSheets)
            fz = zipfile.ZipFile(path,'r') #读取xmind-图片
            ALL_TOPICS_WORKBOOK = getAllTopics_Workbook(sheets)
            ALL_IDS_WORKBOOK = [x.getID() for x in ALL_TOPICS_WORKBOOK]
            for tSheet in targetSheets:
                sheetcounter += 1
                if not func_AutoMode:
                    pLabel.setText(str(pathcounter)+u'/'+str(pathnum)+u':'+str(sheetcounter)+u'/'+str(sheetnum))
                s2d = deckComparator(tSheet,self.FullMode)
                init_Sheet = s2d.init_Sheet
                s2d.run()
            fz.close() #结束读取xmind图片
        if globalPrinter:
            showText(globalPrinter)
            if globalPrinter.find(u'被删除') != -1:showInfo(u'注意：有备注笔记被删除！')
            globalPrinter = ''
        else:
            showInfo(u'无文件变动')
        return 


##########################################
#
# 散功能
#

def ObjectTitleFilter(mark):
    def resolver (o): #闭包
        str1 = o.getTitle()
        if not str1:
            str1 = MULTIMEDIA_TEXT
        if str1.find(mark) == -1:
            return (False)
        else:return(True)
    return(resolver)

def getAllTopics_Workbook(targetSheets):
    tlist = []
    for tSheet in targetSheets:
        init_Sheet = SheetParser(tSheet)
        tlist.extend(init_Sheet.getAllTopics())
    return tlist

def ankistrLineBreak(lst):
    if lst:
        if len(lst) >1:
            new_lst = [lst[0]]
            for item in lst[1:]:
                new_item = u'<div>'+str(item) + u'</div>'
                new_lst.append(new_item)
            return(''.join(new_lst))
        else:
            return(lst[0])
    else:
        return('')
        
        
        

#########################散功能分割线########################
ALL_TOPICS = []

class SheetParser(object):
    
    def __init__(self, sheet):
        self.sheet = sheet
        self.RootTopic = sheet.getRootTopic()
        self.RootTitle = self.RootTopic.getTitle()
        self.ALL_TOPICS = self.getAllTopics()
        self.ALL_TOPICSID = [x.getID() for x in self.ALL_TOPICS]

    def __walkData(self,root_topic,result_list):  
        result_list.append(root_topic)  
      
        #遍历每个子节点  
        children_topic = root_topic.getSubTopics()
        if not children_topic:  
            return  
        for child in children_topic:  
            self.__walkData(child, result_list)
        return  

    def _NotesContentFilter(self,mark):
        '''冻结:暂不可用'''
        def resolver (o): #闭包
            str1 = o.getContent()
            if str1.find(mark) == -1:
                return (False)
            else:return(True)
        return(resolver)

    def getAllTopics(self):    
        result_list = []
        self.__walkData(self.RootTopic, result_list)
        return result_list

    def getTargetTopics(self):
        TargetTopics = list(filter(ObjectTitleFilter(TransMark),self.ALL_TOPICS))
        return TargetTopics

    def getFreeNotes(self,allTopics):
        '''冻结:暂不可用'''
        allNotes = [x for x in [topic.getNotes() for topic in allTopics] if x is not None]
        FreeNotes = list(filter(self._NotesContentFilter(TransMark),allNotes))
        return FreeNotes

    def getRelationshipTopicsId(self):
        relationships =  self.sheet._getRelationships()
        if relationships:
            relist = relationships.childNodes
            rel_id_list = []
            for relationship in relist:
                rel_element = RelationshipElement(relationship,self.RootTopic.getOwnerWorkbook())
                rel_id_list.append([rel_element.getEnd1ID(),rel_element.getEnd2ID()])
            if rel_id_list:
                return rel_id_list
        else:return []

   
class TargetTopicParser(object):
    '''
    目标节点处理
    将节点解析,并格式化为field
    包含模块: 
        节点解析:
            getDirectory 获取节点路径
            getOrphanList 获取平行的节点名称
            getChild 获取子节点的所有内容
            getGrandChild 获取孙节点的所有内容(根据markerref确定深度)
            getHyperLink
            getImages
            getSummary
            getTag
            getRelationshipTopics
        格式化:
            

    '''
    def __init__(self,Topic):
        self.Topic = Topic
        self.Title = Topic.getTitle()
        self.ID = Topic.getID()
        self.styleid = Topic.getAttribute('style-id')
        self.OwnerRootTopic = Topic.getOwnerSheet().getRootTopic()

    #节点解析
    #########################################
    def _NodeTypeFilter(self,node):
        if node.nodeName == 'topic':
            return True
    def _getTitle(self,n):
        node= Node(n).getFirstChildNodeByTagName(const.TAG_TITLE)
        text = []
        for node in node.childNodes:
            if node.nodeType == DOM.Node.TEXT_NODE:
                text.append(node.data)

        if not len(text) > 0:
            return 

        text = "\n".join(text)
        return text
    def __walkDataBackward(self,root_node,level,result_list):  
        result_list.append(root_node)
        parent_node= root_node.parentNode
        if not parent_node:  
            return  
        self.__walkDataBackward(parent_node, level + 1, result_list)
        return  
    def _convertFormat(self,list,mark="-",isMain=False):
        maxLength = max([len(x) for x in list])
        last = list[-1]
        list.pop(-1)
        nlist = ''
        for item in list:
            nlist += item
            #一段话换行
            if isMain == True and maxLength >= AMaxLength:
                nlist += '<br>'
            else:
                nlist += mark
        nlist += last
        #str_convert = ''.join(nlist)
        return(nlist)
    def __walkDataTitleForward(self,root_topic,level,depth,result_list):  
        #getGrandChild专用
        if level >1:
            result_list.append((level-2) * LevelMark + LevelMarkEnd + root_topic.getTitle())  
        else:
            result_list.append(root_topic.getTitle())  
             
        children_topic = root_topic.getSubTopics()
        if not children_topic:  
            return  
        if depth:
            if level == depth:
                return
        for child in children_topic:  
            self.__walkDataTitleForward(child, level +1 ,depth, result_list)
        return  

    def _walkDataForward(self,root_topic,level,result_list):
        result_list.append(root_topic)
        children_topic= root_topic.getSubTopics()
        if not children_topic:  
            return  
        if level == TIMESTAMP_MAXDEPTH:
            return
        for child in children_topic:
            self._walkDataForward(child,level+1,result_list)
        return

    def _DepthRecongizer(self):
        markers = self.Topic.getMarkers()
        if markers:
            if len(markers) == 1:
                markerid = markers[0].getMarkerId().name
                character = MarkerID_num[markerid]
                #预备以后加入其它的定义符
                if type(character) == type(1):
                    return character
    def _getNotes(self):
        notes = self.Topic.getNotes()
        if notes:
            return notes.getContent()  
    def getChildNodesByTagName(self, inode, tag_name):
        """
        Search for all children with specified tag name under passed DOM
        implementation, instead of all descendants
        """
        child_nodes = []
        for node in inode.childNodes:
            if node.nodeType == node.TEXT_NODE:
                continue

            if node.tagName == tag_name:
                child_nodes.append(node)

        return child_nodes

    def _intRange(self,str):
        format_str = str.replace("(","").replace(")","").split(",")
        if len(format_str) == 2:
            f_int = [int(x) for x in format_str]
            return f_int
        else:
            print "Error:_intRange method has more than two numbers."

    def getParentTitleList(self):
        #获取节点路径
        level = 1 #节点的深度从1开始  
        result_list = []
        self.__walkDataBackward(self.Topic._node, level, result_list)
        targetNodes = list(filter(self._NodeTypeFilter,result_list))
        targetNodesTitle = list(map(self._getTitle,targetNodes))[::-1][1:]
        return (targetNodesTitle)

    def getDirectory(self):  
        targetNodesTitle = self.getParentTitleList()
        if targetNodesTitle:
            if targetNodesTitle[-1].find(start_ClozeMark) == -1:
                return self._convertFormat(targetNodesTitle)
            else:
                return self._convertFormat(targetNodesTitle[:-1])

    def getOrphanList(self):
        parent_node = self.Topic._node.parentNode
        orphanNodes = parent_node.childNodes
        orphanTitles = [self._getTitle(orphanNode) for orphanNode in orphanNodes]
        return orphanTitles

    def getChildsList(self):
        if self.Topic.getSubTopics():
            childTitles = []
            for topic in self.Topic.getSubTopics():
                title = topic.getTitle()
                if title:
                    childTitles.append(title)
                else:
                    childTitles.append('')
            e_childTitles = filter(lambda x:x.find(ExcludeMark)== -1 , childTitles)
            return e_childTitles

    def getChilds(self,mark,isMain=False):
        #isMain参数表示调用的方法是否为QA，其他(HYPERLINK,GRANDCHILDS调用它时默认为False)
        childList = self.getChildsList()
        if childList:
            return self._convertFormat(childList,mark,isMain).replace(TransMark,'')
        else:
            return self._getNotes()


    def getGrandChilds(self):
        #markerref = depth
        depth = self._DepthRecongizer()
        if depth:
            level = 0
            result_list = []
            self.__walkDataTitleForward(self.Topic,level,depth,result_list)
            del result_list[0]
            return ankistrLineBreak(result_list)

    def getHyperLink(self):
        hyperlink = self.Topic.getAttribute(const.ATTR_HREF)
        if hyperlink:
            if hyperlink.find(const.TOPIC_PROTOCOL) != -1:#判断是否为其他标题
                if hyperlink[7:] in ALL_IDS_WORKBOOK:#判断是否指向的特殊标题-待开发（独立标题无法识别）
                    topic_index = ALL_IDS_WORKBOOK.index(hyperlink[7:])
                    hl_topic = ALL_TOPICS_WORKBOOK[topic_index]
                    return hl_topic,True
                else:
                    return None,False
            else:
                return hyperlink,False
        else:
            return None,False

    def getImages(self):
        '''
        注意最后替换解压路径为Anki用户目录
        '''
        #获取不支持项就照这个来
        imgnode = self.Topic.getChildNodesByTagName(TAG_IMG)
        if imgnode:
            imgname = imgnode[0].getAttribute(ATTR_IMGSRC).replace(STR_IMG,'')
            fz.extract(imgname, AnkiRoot_absPath+AnkiMedia_relPath)
            return imgname

    def getLabels(self):
        '''
        获取目标主题的标签
        '''
        labelsNode = self.Topic.getChildNodesByTagName(TAG_LABELS)
        if labelsNode:
            labelNodes = self.getChildNodesByTagName(labelsNode[0],TAG_LABEL)
            labels = []
            for labelNode in labelNodes:
                label = labelNode.toxml().replace("<"+TAG_LABEL+">","").replace("</"+TAG_LABEL+">","")
                labels.append(label)
            return labels


    def getSummary(self):
        sumsnode = self.Topic.getChildNodesByTagName(TAG_SUMMARIES)
        if sumsnode:
            subTopics = self.Topic.getSubTopics(TOPIC_SUMMARY)
            sumnodes = self.getChildNodesByTagName(sumsnode[0],TAG_SUMMARY)
            t_and_r = []
            for sumnode in sumnodes:
                sum_range = self._intRange(sumnode.getAttribute("range"))
                sum_topicid = sumnode.getAttribute("topic-id")
                for subTopic in subTopics:
                    st_id = subTopic.getID()
                    if st_id == sum_topicid:
                        t_and_r.append([subTopic,sum_range])
            return t_and_r


    def getRelationshipTopics(self):
        extern = init_Sheet
        rel_list = []
        rel_id =None
        for rel_ids in extern.getRelationshipTopicsId() :
            if self.ID == rel_ids[0]:
                rel_id = rel_ids[1]
            if self.ID == rel_ids[1]:
                rel_id = rel_ids[0]
            if rel_id and (rel_id in extern.ALL_TOPICSID) :#后者是防止出现特殊属性的Topic,出现就忽略
                rel_list.append(extern.ALL_TOPICS[extern.ALL_TOPICSID.index(rel_id)])
        if len(rel_list):
            new_li=list(set(rel_list))
            return new_li
    
    #格式化
    ###########################################
    def _delMarks(self,str1):
        return str1.replace(TransMark,'').replace(MultiMark,'').replace(ExcludeMark,'')

    def _formatCloze_Q(self,str1):

        countfront = str1.count(start_ClozeMark)
        countback = str1.count(end_ClozeMark)
        if countfront == countback:
            if countfront > 0: #判断Question有括号
                if self.Title.find(MultiMark) == -1: #判断是否有多空标记
                    f_ClozeQ = str1.replace(start_ClozeMark,"{{c1::").replace(end_ClozeMark,"}}")
                else:
                    for x in range(1,countfront+1):
                        str1  = str1.replace(start_ClozeMark,"{{c"+str(x)+"::",1)
                    f_ClozeQ = str1.replace(end_ClozeMark,"}}")
            else:
                f_ClozeQ = str1
            return f_ClozeQ,countfront
        else:
            showInfo("错误：找到未成对的方括号!\n"+str1)
            raise Exception(u'方括号成对错误')

    def _formatCloze_A(self,str1,QCount):

        countfront = str1.count(start_ClozeMark)
        countback = str1.count(end_ClozeMark)
        if countfront == countback:
            if countfront > 0: #判断Answer有括号
                if self.Title.find(MultiMark) == -1: #判断是否有多空标记
                    f_ClozeA = str1.replace(start_ClozeMark,"{{c1::").replace(end_ClozeMark,"}}")
                else:
                    for x in range(QCount+1,countfront+QCount+1):
                        str1  = str1.replace(start_ClozeMark,"{{c"+str(x)+"::",1)
                    f_ClozeA = str1.replace(end_ClozeMark,"}}")
            else:
                if self.Title.find(MultiMark) == -1: #判断是否有多空标记
                    f_ClozeA = "{{c1::"+str1+"}}"
                else:
                    f_ClozeA = "{{c"+str(QCount+1)+"::"+str1+"}}"
        else:
            print("错误：找到未成对的方括号")
            print("错误内容:"+str1)
        return f_ClozeA

    def field_QA(self):
        '''
        Title&Childs
        在获取到单个节点形成的空时判定markerref是否为 1 ,如果为1则不再读取子节点,仅父节点成卡片
        '''
        if self.getChildsList():
            fQstr,QCount = self._formatCloze_Q(self.Title)
            fAstr = self._formatCloze_A(self.getChilds(ChildsSeparator,isMain=True),QCount)
            #判断是否需要在问题前生成补充问题
            if len(fQstr) <= QMinLength:
                parentTitles = self.getParentTitleList()
                if parentTitles:
                    if parentTitles[-1] == fQstr:
                        if len(parentTitles) >= 2:
                            fQstr = "(" + parentTitles[-2] + ")" + fQstr
                    else:
                        fQstr = "(" + parentTitles[-1] + ")" + fQstr
            #判断问题长度是否过长
            if len(fQstr) >= QMaxLength or fAstr.find('<br>') != -1:
                field_Data = fQstr + QASeparator +'<br>'+ fAstr
            else:
                field_Data = fQstr + QASeparator + fAstr
            #showInfo(field_Data)
            markers = self.Topic.getMarkers()
            if markers:
                #判断是否深挖
                markerid = markers[0].getMarkerId().name
                if MarkerID_num[markerid] == 1:
                    return self._delMarks(self.Title)
                else:
                    return self._delMarks(field_Data)
            else:
                return self._delMarks(field_Data)
        else:
            return self._delMarks(self._formatCloze_Q(self.Title)[0])

    def field_DIR(self):
        format_dir = self._delMarks(self.getDirectory())
        return format_dir
        
    def field_MINDMAP(self):
        '''
        getOrphanList;getChilds;getDirectory[-1]
        '''
        result_list = []
        self.__walkDataBackward(self.Topic._node, 1, result_list)
        targetNodes = list(filter(self._NodeTypeFilter,result_list))
        if len(targetNodes) >= 2:
            ParentTitle = list(map(self._getTitle,targetNodes))[1]
        else: ParentTitle = 'Root'
        OrphanTitles = self.getOrphanList() 
        ChildTitles =self.getChildsList()
        loc = OrphanTitles.index(self.Title)

        #html格式化
        html_head = "<ul class=\"tree\"><li>" + ParentTitle +"<ul>"
        html_end = "</ul></li></ul>"

        level2 = "<ul>"
        if ChildTitles:
            for ct in ChildTitles:
                if not ct:
                    ct = MULTIMEDIA_TEXT
                format_ct = "<li>" + ct + "</li>"
                level2 += format_ct
            level2 += "</ul>"

        level1 = ""
        counter = 0
        for ot in OrphanTitles:
            if not ot:
                ot = MULTIMEDIA_TEXT
            if counter == loc:
                format_ot = "<li>" + ot + level2 + "</li>"
                level1 += format_ot
            else:
                format_ot = "<li>" + ot + "</li>"
                level1 += format_ot
            counter += 1

        html_merge = html_head + level1 +html_end

        return self._delMarks(html_merge)
        

    def field_GRANDCHILDS(self):
        grdchild = self.getGrandChilds() #最终
        if grdchild:
            return grdchild
        else:return(u'')

    def field_HYPERLINK(self):
        ##HyperLink
        hyperLink,TorF = self.getHyperLink()
        if hyperLink:
            if TorF:
                hl_topic = TargetTopicParser(hyperLink)
                if hl_topic.getChildsList():
                    field_Data = hl_topic.Title + QASeparator + hl_topic.getChilds(ChildsSeparator)
                    markers = hl_topic.Topic.getMarkers()
                    if markers:
                        #判断是否深挖
                        markerid = markers[0].getMarkerId().name
                        if MarkerID_num[markerid] == 1:
                            return hl_topic._delMarks(hl_topic.Title)
                        else:
                            return hl_topic._delMarks(field_Data)
                    else:
                        return hl_topic._delMarks(field_Data)
                else:
                    return hl_topic._delMarks(hl_topic.Title)
            else:
                return hyperLink
        else:return(u'')

    def field_IMAGE(self):
        ##Images
        image = self.getImages()
        if image:
            image = "<div><img src=\"" + image + "\" /></div>" #最终
            return (image)
        else:return(u'')

    def field_SUMMARY(self):
        ##Summary
        sum_hybrids =  self.getSummary()
        if sum_hybrids:
            sum_strs = []
            for sum_hybrid in sum_hybrids:
                str1 = sum_hybrid[0].getTitle()
                if not str1:
                    str1 = ''
                subt = self.Topic.getSubTopics()
                target_subt = []
                for x in range(sum_hybrid[1][0],sum_hybrid[1][1]+1):
                    target_subt.append(subt[x].getTitle())
                str2 = string.join(target_subt,SummaryConnector)
                sum_str = str2+SummaryEqualMark+str1
                sum_strs.append(sum_str)
            sum_merge = ankistrLineBreak(sum_strs) #最终
            return sum_merge
        else:return(u'')

    def field_RELATIONSHIP_Q(self):
        ##Relationship
        rel_topics = self.getRelationshipTopics()
        if rel_topics:
            rel_titles = [x.getTitle() for x in rel_topics]
            rel_merge = string.join(rel_titles,ChildsSeparator) #最终
            return self._delMarks(rel_merge)
        else:return(u'')

    def field_RELATIONSHIP_A(self):
        rel_str_list = []
        rel_topics = self.getRelationshipTopics()
        if rel_topics:
            for rel_topic in rel_topics:
                str1 = rel_topic.getTitle()
                childTopics = rel_topic.getSubTopics()
                if childTopics:
                    childTitles = [x.getTitle() for x in childTopics]
                    str2 = string.join(childTitles,ChildsSeparator)
                    str_merge = str1 + QASeparator + str2
                else:
                    str_merge = ''
                rel_str_list.append(str_merge)
            rel_str_merge = ankistrLineBreak(rel_str_list)
            return self._delMarks(rel_str_merge)
        else:return(u'')

    def field_TIMESTAMP(self):  
        result_list = []
        self._walkDataForward(self.Topic,0,result_list)
        if result_list:
            ts_list = [x.getAttribute('timestamp') for x in result_list]
            ts_merge = string.join(ts_list,IDSeparator)
            return ts_merge

    def field_ID(self):
        '''
        格式:根节点ID(首位)+子孙节点ID
        '''
        result_list = []
        self._walkDataForward(self.Topic,0,result_list)
        if result_list:
            id_list = [x.getID() for x in result_list]
            id_merge = string.join(id_list,IDSeparator)
            imgnode = self.Topic.getChildNodesByTagName(TAG_IMG)
            return id_merge
    
    def field_LABELS(self):
        labels = self.getLabels()
        if labels:
            str_labels = string.join(labels,ChildsSeparator)
            return str_labels
        else:
            return ''
        

    #综合
    def params_Constructor(self):
        params = {}
        params['fields'] = {}
        params['deckName'] = self.OwnerRootTopic.getTitle().replace(SubMark,"::")
        params['modelName'] = modelName
        params['fields']['QA'] = self.field_QA()
        params['fields']['DIR'] = self.field_DIR()
        params['fields']['RELATIONSHIP_Q'] = self.field_RELATIONSHIP_Q()
        params['fields']['RELATIONSHIP_A'] = self.field_RELATIONSHIP_A()
        params['fields']['MINDMAP'] = self.field_MINDMAP()
        params['fields']['ID'] = self.field_ID()
        params['fields']['TIMESTAMP'] = self.field_TIMESTAMP()
        params['fields']['GRANDCHILDS'] = self.field_GRANDCHILDS()
        params['fields']['HYPERLINK'] = self.field_HYPERLINK()
        params['fields']['IMAGE'] = self.field_IMAGE()
        params['fields']['SUMMARY'] = self.field_SUMMARY()
        params['fields']['LABELS'] = self.field_LABELS()
        return params

#
# AnkiNoteParams
#

class AnkiNoteParams:
    def __init__(self, params):
        self.deckName = params.get('deckName')
        self.modelName = params.get('modelName')
        self.fields = params.get('fields', {})
        self.tags = params.get('tags', [])
    
    def verifyString(self,string):
        t = type(string)
        return t == str or t == unicode


    def verifyStringList(self,strings):
        for s in strings:
            if not self.verifyString(s):
                return False
        return True

    def validate(self):
        '''
        测试部分
        print self.deckName
        print self.modelName
        print self.fields
        print self.tags
        print u'vdeckname',self.verifyString(self.deckName)
        print u'vmodelname',self.verifyString(self.modelName)
        print u'vfields=dict',type(self.fields)
        print u'vfldkeys',self.verifyStringList(list(self.fields.keys()))
        print u'vfldvalues',self.verifyStringList(list(self.fields.values()))
        print u'vtags=list',type(self.tags)
        print u'vtags',self.verifyStringList(self.tags)
        '''
        #showInfo(u'vtags'+ str(self.verifyStringList(self.tags)))
        return (
            self.verifyString(self.deckName) and
            self.verifyString(self.modelName) and
            type(self.fields) == dict and self.verifyStringList(list(self.fields.keys())) and self.verifyStringList(list(self.fields.values())) and
            type(self.tags) == list and self.verifyStringList(self.tags)
        )

#
# AnkiBridge
#

class AnkiBridge:
    def addNote(self, params):
        collection = self.collection()
        if collection is None:
            return

        note = self.createNote(params)
        if note is None:
            return

        self.startEditing()
        collection.addNote(note)
        collection.autosave()
        self.stopEditing()

        return note.id


    def createNote(self, params):#
        collection = self.collection()
        if collection is None:
            return

        model = collection.models.byName(params.modelName)
        if model is None:
            return

        deck = collection.decks.byName(params.deckName)
        if deck is None:
            return

        note = anki.notes.Note(collection, model)
        note.model()['did'] = deck['id']
        note.tags = params.tags

        for name, value in params.fields.items():
            if name in note:
                note[name] = value

        doe = note.dupeOrEmpty()
        if not doe or doe == 2:
            return note


    def startEditing(self):#
        self.window().requireReset()


    def stopEditing(self):
        if self.collection() is not None:
            self.window().maybeReset()


    def window(self):
        return aqt.mw


    def collection(self):#
        return self.window().col


    def media(self):
        collection = self.collection()
        if collection is not None:
            return collection.media


    def modelNames(self):
        collection = self.collection()
        if collection is not None:
            return collection.models.allNames()


    def modelFieldNames(self, modelName):
        collection = self.collection()
        if collection is None:
            return

        model = collection.models.byName(modelName)
        if model is not None:
            return [field['name'] for field in model['flds']]


    def deckNames(self):
        collection = self.collection()
        if collection is not None:
            return collection.decks.allNames()

#
# deck/sheet比较器
#


class deckComparator(object):
    '''
    本模块对接deck和Sheet
    包含功能:
        获取部分:
            Anki部分:获取目标deck的所有ID
            XMind部分:获取目标sheet的所有ID
        比对部分:(注意nid与filed['ID']的对应情况)
            ID交集:求XA的ID交集→不变Anki条目
            A 差 交:AnkiID与ID交集的差集→删除Anki条目
            X 差 交:XMindID与ID交集的差集→新增Anki条目
        操作部分:
            删除Anki条目:获取nid,删除
            新增Anki条目:获取新增的params,用ankiconnect传入Anki
            不变Anki条目:验证条目TS是否相等,不相等用mw修改数据(可参考旧版)
        回显部分:
            输出删除条目内容,新增条目内容,修改条目内容(TS改变的),不变条目个数

    '''
    def __init__(self, tSheet,FullMode):
        self.init_Sheet = SheetParser(tSheet)
        self.TargetTopics =  self.init_Sheet.getTargetTopics()
        self.anki = AnkiBridge()
        self.xdname = self.init_Sheet.RootTopic.getTitle().replace(SubMark,"::")
        self.counter = 0
        self.xmindTotal = len(self.TargetTopics)
        self.FullMode = FullMode
        if not func_AutoMode:
            pBar.setMinimum(0)
            pBar.setMaximum(self.xmindTotal) 
        return 
    
    #获取部分
    #########

    def Anki_check(self):
        '''
        检查是否存在目标deckName,没有就加一个
        '''
        did = mw.col.decks.id(self.xdname)#调用已有函数 "Add a deck with NAME. Reuse deck if already exists. Return id as int."
        return did

    def getAllXMindformatIDs(self):
        '''
        XMind部分:获取目标sheet的所有ID
        '''
        fIDs = []
        for TTopic in self.TargetTopics:
            init_TTopic = TargetTopicParser(TTopic)
            fIDs.append(init_TTopic.field_ID())
        return fIDs

    def getAllAnkiformatIDs(self):
        '''
        Anki部分:获取目标deck的所有ID
        '''
        did = self.Anki_check()
        m = mw.col.models.byName(modelName)
        emid = m["id"]
        nids = mw.col.models.nids(m)
        cidlist = mw.col.decks.cids(did)
        nidlist = []
        for cid in cidlist:
            ecard = mw.col.getCard(cid)
            enid = ecard.nid
            enote = mw.col.getNote(enid)
            if enote.mid == emid:
                nidlist.append(ecard.nid)
        nids = set(nidlist)
        if nids:#过滤手动内容
            filter_nids = []
            filter_fld_ID_Data = []
            for nid in nids:
                note = mw.col.getNote(nid)
                if fld_ID_name in note.keys():
                    fld_ID = note[fld_ID_name]
                    if fld_ID:
                        filter_nids.append(nid)
                        filter_fld_ID_Data.append(fld_ID)
            return filter_fld_ID_Data,filter_nids
        else:
            return None,None

    #比对部分
    #########
    def dispatchID(self):
        '''
        比对部分:(注意nid与filed['ID']的对应情况)
            ID交集:求XA的ID交集→不变Anki条目
            A 差 交:AnkiID与ID交集的差集→删除Anki条目
            X 差 交:XMindID与ID交集的差集→新增Anki条目
            对比差集求根节点相同的一对→子节点有改变的Anki条目
        '''
        self.pairs = {}
        AnkiIDs,Ankinids = self.getAllAnkiformatIDs()
        XMindIDs = self.getAllXMindformatIDs()
        if Ankinids:
            set_XIA = set(AnkiIDs).intersection(set(XMindIDs))#→不变Anki条目
            XIA = list(set_XIA)
            A_XIA = list(set(AnkiIDs).difference(set_XIA))#AnkiID与ID交集的差集→删除Anki条目
            X_XIA = list(set(XMindIDs).difference(set_XIA))#XMindID与ID交集的差集→新增Anki条目
            #对比差集求根节点相同的一对→子节点有改变的Anki条目
            for itemA in A_XIA:
                rootid_A = itemA.split(IDSeparator,1)[0]
                for itemX in X_XIA: 
                    rootid_X = itemX.split(IDSeparator,1)[0]
                    if rootid_A == rootid_X:
                        self.pairs[XMindIDs.index(itemX)] = Ankinids[AnkiIDs.index(itemA)]
                        A_XIA.remove(itemA)
                        X_XIA.remove(itemX)
            for x in XIA:self.pairs[XMindIDs.index(x)] =Ankinids[AnkiIDs.index(x)]#相同条目成对
            self.A_rem_nids = map(lambda x:Ankinids[AnkiIDs.index(x)],A_XIA)#要删除anki条目的nid
            self.X_add_nums = map(lambda x:XMindIDs.index(x),X_XIA)#要增加条目的序号
        else:
            self.X_add_nums = range(0,len(XMindIDs))
            self.A_rem_nids = None

        return

    #操作部分
    #########

    def backupRemNotes(self,nids):
        '''
        仅备份有手动笔记的项
        '''
        global globalPrinter
        path = AnkiRoot_absPath+ u'\\x2a-deleted.txt'
        existed = os.path.exists(path)

        warningMark = False

        with open(path, "a") as f:
            if not existed:
                f.write("QA\tdeleted_items\n")
            for nid in nids:
                fld_exist = False
                fld_Data = []
                note = mw.col.getNote(nid)
                fld_Data.append(note['QA'])
                for fld_name in MANUAL_FLD_NAMES:
                    fld_Data.append(note[fld_name])
                    if note[fld_name]:
                        fld_exist = True
                        warningMark = True
                if fld_exist:
                    f.write("\t".join(fld_Data).encode("utf8"))
                    f.write("\n")
        if warningMark:
            globalPrinter += u'注意：有备注笔记被删除！'

    def overlayNote(self,note,init_topic):
        note['QA'] = init_topic.field_QA()
        note['DIR'] = init_topic.field_DIR()
        note['RELATIONSHIP_Q'] = init_topic.field_RELATIONSHIP_Q()
        note['RELATIONSHIP_A'] = init_topic.field_RELATIONSHIP_A()
        note['MINDMAP'] = init_topic.field_MINDMAP()
        note['ID'] = init_topic.field_ID()
        note['TIMESTAMP'] = init_topic.field_TIMESTAMP()
        note['GRANDCHILDS'] = init_topic.field_GRANDCHILDS()
        note['HYPERLINK'] = init_topic.field_HYPERLINK()
        note['IMAGE'] = init_topic.field_IMAGE()
        note['SUMMARY'] = init_topic.field_SUMMARY()
        note['LABELS'] = init_topic.field_LABELS()
        note.flush()
        return

    def Anki_remNote(self):
        '''
        删除Anki条目:获取nid,删除
        '''
        del_num = 0
        del_results = []

        if self.A_rem_nids:
            del_num = len(self.A_rem_nids)
            for nid in self.A_rem_nids:
                note = mw.col.getNote(nid)
                del_results.append(note[fld_QA_name])
            #备份笔记
            self.backupRemNotes(self.A_rem_nids)
            #删除笔记
            mw.col.remNotes(self.A_rem_nids)
            mw.col.reset()
            mw.reset()
        return (del_num,del_results)

    def Anki_addNote(self):
        '''
        新增Anki条目:获取新增的params,检查rem项中无相似项后，用ankiconnect传入Anki
        '''
        addTopics = [self.TargetTopics[i] for i in self.X_add_nums]
        suc_results = []
        fail_results = []
        suc_num = 0
        fail_num = 0
        remNotes_QA = []
        remNotes_DIR = []
        
        #列出所有即将被删除的Note
        if self.A_rem_nids:
            remNotes = [mw.col.getNote(nid) for nid in self.A_rem_nids]
            remNotes_QA = [note['QA'] for note in remNotes]
            remNotes_DIR = [note['DIR'] for note in remNotes]

        #新增条目
        for addTopic in addTopics:
            self.counter += 1#计数加一
            dup = False
            if not func_AutoMode:
                pBar.setValue(self.counter)#设置进度条
            init_addTopic = TargetTopicParser(addTopic)

            #检查与remNotes项中的相似度
            addNote_DIR = init_addTopic.field_DIR()
            addNote_QA = init_addTopic.field_QA()
            if self.A_rem_nids:
                QARatios = [sm(None,remNote_QA,addNote_QA).ratio() for remNote_QA in remNotes_QA]
                DIRRatios = [sm(None,remNote_DIR,addNote_DIR).ratio() for remNote_DIR in remNotes_DIR]
                maxQARatio = max(QARatios)
                if maxQARatio >=similarityAimRatio:
                    i = QARatios.index(maxQARatio)
                    if DIRRatios[i] >=dir_similarityAimRatio:
                        #符合DIR&QA相似度，覆盖
                        self.overlayNote(note,init_addTopic)
                        #删除nid等项
                        self.A_rem_nids.pop(i)
                        remNotes.pop(i)
                        remNotes_QA.pop(i)
                        remNotes_DIR.pop(i)
                        dup = True
                        #回显
                        suc_results.append(u'（覆盖）'+ addNote_QA)
            if not dup:
                #如果不相似，则生成param传送给ankiconnect
                params = AnkiNoteParams(init_addTopic.params_Constructor())
                if params.validate():
                    suc_num += 1
                    self.anki.addNote(params)
                    suc_results.append(addNote_QA)
                else:
                    fail_num += 1
                    fail_results.append(addNote_QA)
        return (suc_num,fail_num,suc_results,fail_results)

    def Anki_checkNoteTS(self):
        '''
        不变Anki条目:验证条目TS是否相等,不相等用mw修改数据(可参考旧版)
        '''
        check_len = len(self.pairs)
        changed_len = 0
        changed_item = []
        for x,a in self.pairs.items():
            init_chkTopic = TargetTopicParser(self.TargetTopics[x])
            xTS = init_chkTopic.field_TIMESTAMP()
            note = mw.col.getNote(a)
            aTS = note[fld_TIMESTAMP_name]
            self.counter += 1#计数加一
            if not func_AutoMode:
                pBar.setValue(self.counter)#设置进度条
            if xTS != aTS or self.FullMode:
                #回显数据
                changed_len += 1
                fld_QA = init_chkTopic.field_QA()
                changed_item.append(fld_QA)
                #修改note内容
                self.overlayNote(note,init_chkTopic)
        return (changed_len,check_len-changed_len,changed_item)


    #回显部分
    #########
    def formatString(self,list):
        return ''.join([u'    '+ x[:echoChrLength]+ u'...\n' for x in list if list])

    def echo2Anki(self,delinf,addinf,chkinf):
        del_num,del_results = delinf
        add_suc_num,add_fail_num,add_suc_results,add_fail_results = addinf
        changed_num,unchanged_num,changed_result = chkinf
        str1 = u'XMind画布: '+ self.xdname + u' 包含'+ str(self.xmindTotal) + u'个目标项\n'
        divideLine = u'---------------------------------\n'
        str_changed1 = u'修改项：'+ str(changed_num) + u'个，未修改项：'+ str(unchanged_num) + u'个\n\n'
        str_add1 = u'新增项：'+ str(add_suc_num) + u'个\n\n'
        str_del1 = u'删除项：'+ str(del_num) + u'个\n\n'
        str_changed2 = self.formatString(changed_result)
        str_add2_suc = self.formatString(add_suc_results)
        str_add2_fail =  self.formatString(add_fail_results)
        str_del2 =  self.formatString(del_results)
        merge_str = str1 + divideLine +str_changed1 + str_changed2 + str_add1 + str_add2_suc + str_del1 + str_del2
        if changed_num == 0 and add_suc_num == 0 and del_num == 0:
            return None
        else:
            return merge_str

    def run(self):
        global globalPrinter
        self.dispatchID()#分流类型
        #注意：先新增再删除，新增中有相似度检验
        addinf = self.Anki_addNote()#类型:新增Anki条目
        delinf = self.Anki_remNote()#类型:删除Anki条目
        chkinf = self.Anki_checkNoteTS()#类型:不变Anki条目
        echos = self.echo2Anki(delinf,addinf,chkinf) #汇总回显
        if AutoUpdateYN == 0:
            if echos:
                globalPrinter += echos
        else:
            showInfo('自动模式工作中')
        return






