#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2014-11-14 08:27:44
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import os
import _winreg
from bs4 import BeautifulSoup,NavigableString,Tag
import re
import urllib2
import codecs
import logging
import time
from functools import wraps

import multiprocessing
import Queue
import threading

global code
code='utf8'

class NetArticle:
    def __init__(self):
        self.url=""
        self.titleimg=""
        self.title=""
        self.posttime=""
        self.category=""
        self.keywords=""
        self.article=""
        self.img=""
        
    def __str__(self):
        return "%s\n%s\n%s"%(self.title.encode(code),self.category.encode(code),self.keywords.encode(code))

    def make_article(self,folderpath):
        fix=unicode("\\%s.txt"%self.title)
        fix
        path=folderpath+fix
        f=codecs.open(path,'w',code)
        f.write("posttime:%s\r\n"%self.posttime)
        f.write("category:%s\r\n"%self.category)
        f.write("keywords:%s\r\n"%self.keywords)
        f.write("articurl:%s\r\n"%self.url)
        f.write("\r\n\r\n")
        f.write(self.article)
        f.close()
        print "%s Done well!"%self.title.encode(code)

def readpage_deco(func):
    @wraps(func)
    def wrapper(url,page):
        if page is None:
            page=readpage(url)
            if page=="":
                return None

        res=func(url,page)
        return res
    return wrapper

def timeused_deco(func):
    def wrapper(*args, **kwargs):
        strcolock=round(time.clock(),2)
        res=func(*args, **kwargs)        
        seccolock=round(time.clock(),2)-strcolock
        print "%s(%s) timeused: %ss"%(func.func_name,args[0],seccolock)
        return res
    return wrapper

@timeused_deco
def readfile(filepath):
    f=open(filepath,'r')
    filecontent=""
    try:
        filecontent=f.read()
    except:
        pass
    finally:
        f.close()
    return filecontent

@timeused_deco
def readpage(pageurl):
    # proxy_support = urllib2.ProxyHandler({'http':'http://XX.XX.XX.XX:XXXX'})
    # opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    # urllib2.install_opener(opener)
    content=""
    i_headers = {"User-Agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.1) Gecko/20090624 Firefox/3.5", \
                    "Referer": 'http://www.baidu.com'}
    req = urllib2.Request(pageurl, headers=i_headers)
    try:
        content= urllib2.urlopen(req,timeout=5).read()  #important
    except Exception,e:
        print e
        logging.error("readpage Error:"+pageurl)
    return content

def logconfig(logname='MyArt'):
    logging.basicConfig(filename='%s-log.txt'%logname,\
            level=logging.INFO,format="%(asctime)s-%(levelname)s:%(message)s",datefmt='%d %b %Y,%H:%M:%S')

class Bs4BaseTool:
    def __init__(self):
        self.menu_urllist = []
        self.outputfolder='MyArt'
        self.totallist=[]
        self.baseurl=''
        self.pagerange=range(1,2)
        self.menuurlque=Queue.Queue()
        self.arturlque=Queue.Queue()
        self.artobjque=Queue.Queue()

    def make_desktop_path(self,foldername):
        path=r"c:"
        key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',)
        path=unicode(_winreg.QueryValueEx(key, "Desktop")[0]+"\\%s\\Page_%s"%(self.outputfolder,foldername))

        if not os.path.exists(path):
            os.makedirs(path) #多重路径
        return path

    def make_menulist(self):
        menu_urllist=[]
        menu_urllist=[["%s%s"%(self.baseurl,p),p] for p in self.pagerange]
        return menu_urllist

    @staticmethod
    def parse_menu(menuurl,page=None):
        article_urllist=[]
        #override
        return article_urllist

    @staticmethod
    def parse_article(arturl,page=None):
        #override
        art=NetArticle()
        art.url=arturl
        art.title=title
        art.posttime=time
        art.category=catalog
        art.keywords=keywords
        art.img=img
        art.article=unicode(article,code)
        return art
    
    @staticmethod
    def regx_article(articlestr):
        '''对time3网页进行一些正则处理'''
        result=""
        restr="\r\n"

        patternlist=[]
        patternlist.append(re.compile(r"&nbsp;",re.M))
        patternlist.append(re.compile(r"<img[\S\s]+>",re.M))
        patternlist.append(re.compile(r"<script[\S\s]+>[\S\s]+</script>",re.M))
        patternlist.append(re.compile(r"</?span[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?strong[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?li[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?em[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?ol[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?ul[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?a[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?b[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"</?blockquote[\S\s]*?>",re.M))
        
        patternlist.append(re.compile(r"</?div[\S\s]*?>",re.M))

        patternlist.append(re.compile(r"<p[\S\s]*?>",re.M))
        patternlist.append(re.compile(r"<hr>",re.M))

        patternlist.append(re.compile(r"\s{4,}",re.M))


        for reobj in patternlist:
            articlestr=reobj.sub('',articlestr)

        articlestr=re.compile(r"</p>",re.M).sub(restr,articlestr)
        articlestr=re.compile(r"(\r){1,} ",re.M).sub(restr,articlestr)
        articlestr=re.compile(r"(\n){1,} ",re.M).sub(restr,articlestr)
        articlestr=re.compile(r"(\r\n){2,} ",re.M).sub(restr,articlestr)
        

        return articlestr 

    def menu_worker(self):
        while True:
            try:
                menu_url,pagename=self.menuurlque.get()
                article_urllist=self.parse_menu(menu_url,None)
                if article_urllist is None:
                    logging.error("read_menupage Error:"+menu_url)
                elif len(article_urllist)>0:
                    self.arturlque.put([pagename,article_urllist])
                else:
                    logging.error("parse_menu Error:"+menu_url)
            except Exception as e:
                print e
            finally:
                self.menuurlque.task_done()
                print "-------------menuurlque.task_done------------"
    def article_worker(self):
        while True:
            try:
                pagename,article_urllist=self.arturlque.get()
                folderpath=self.make_desktop_path(pagename)
                for i in range(len(article_urllist)):
                    article_url=article_urllist[i]
                    try:
                        art= self.parse_article(article_url,None)
                        if art is not None:
                            self.artobjque.put([art,folderpath])
                            logging.info("make_article OK:"+art.title)
                    except Exception,e:
                        print e
                        logging.error("parse_article Error:"+article_url)
            finally:
                self.arturlque.task_done()
                print "-------------arturlque.task_done------------"
    def artfile_worker(self):
        while True:
            try:
                art,folderpath=self.artobjque.get()
                art.make_article(folderpath)
            finally:
                self.artobjque.task_done()
                print "-------------artobjque.task_done------------"
    def sp1_creatthread(self):
        concurrency=multiprocessing.cpu_count()
        for _ in range(concurrency):
            thread = threading.Thread(target=self.menu_worker)
            thread.daemon = True
            thread.start()

        for _ in range(concurrency*2):
            thread = threading.Thread(target=self.article_worker)
            thread.daemon = True
            thread.start()

        for _ in range(concurrency):
            thread = threading.Thread(target=self.artfile_worker)
            thread.daemon = True
            thread.start()
    def sp2_addjobs(self):
        self.menu_urllist=self.make_menulist()
        for item in self.menu_urllist:
            self.menuurlque.put(item)
    def sp3_process(self):
        canceled = False
        try:
            self.menuurlque.join() 
            self.arturlque.join() 
            self.artobjque.join() 
        except KeyboardInterrupt: 
            print "canceling..."
            canceled = True

    def parse_start_Thread(self):
        self.sp1_creatthread()
        self.sp2_addjobs()
        self.sp3_process()

    def parse_start(self):
        self.totallist=[]
        self.menu_urllist=[]
        self.menu_urllist=self.make_menulist()

        print "start...menu"
        for menu_url,pagename in self.menu_urllist:
            article_urllist=self.parse_menu(menu_url,None)#IO
            if article_urllist is None:
                logging.error("read_menupage Error:"+menu_url)
            elif len(article_urllist)>0:
                self.totallist.append([pagename,article_urllist])
            else:
                logging.error("parse_menu Error:"+menu_url)

        print "start...page:%s"%len(self.totallist)        
        for i in xrange(len(self.totallist)):
            art=None
            pagename=self.totallist[i][0]
            article_urllist=self.totallist[i][1]
            folderpath=self.make_desktop_path(pagename)#IO

            for j in xrange(len(article_urllist)):
                article_url=article_urllist[j]
                try:
                    art= self.parse_article(article_url,None)#IO
                    art.make_article(folderpath)#IO
                    logging.info("make_article OK:"+art.title)
                except Exception,e:
                    print e
                    logging.error("parse_article Error:"+article_url)
        
class Time3Tool(Bs4BaseTool):
    """scraw articles from timetimetime.com"""
    def __init__(self):
        Bs4BaseTool.__init__(self)
        self.outputfolder='Time3'
        self.baseurl="http://www.timetimetime.net/catalog.asp?cate=2&page="
        self.pagerange=range(1,2)

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_menu(menuurl,page=None):#默认传URL，也可直接传网页内容进行测试
        soup = BeautifulSoup(page,from_encoding='utf8')
        indexbox=soup.find('div', { "class" : "indexbox_l"})
        divlist=indexbox('div',{"class":"left_contant"})
        articlelist=[item.findNext('a',target="_blank") for item in divlist]
        result=[]
        for item in articlelist:
            result.append(item["href"])
        return result

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_article(arturl,page=None):#默认传URL，也可直接传网页内容进行测试
        soup = BeautifulSoup(page,from_encoding='utf8')
        title=soup.find('title').string.split('|')[0].strip()
        keywords=soup.find('meta',{"name":"keywords"})["content"]
        #keywords的另一种获取方法
        # keywords=",".join([item.string for item in info('a', { "class" : "tags"})])
        indexbox=soup.find('div', { "class" : "indexbox_l"})
        info=indexbox.find('div',{"class":"neirongxinxi a9"})
        content=indexbox.find('div',{"class":"neiz1 a7"})
        time=info.find('a',href="#").string
        catalog=info.find('a',title=True).string
        img=content.find('img')["src"]

        content.contents.pop(0)#删除小标题
        innerlink=content.a
        innerlink.extract()#删除文章内连接

        #文章转成指定编码，默认为UTF8
        article=Bs4BaseTool.regx_article(content.renderContents())

        art=NetArticle()
        art.url=arturl
        art.title=title
        art.posttime=time
        art.category=catalog
        art.keywords=keywords
        art.img=img
        art.article=unicode(article,code)
        return art

class ZreadingTool(Bs4BaseTool):
    """docstring for ZreadingTool"""
    def __init__(self):
        Bs4BaseTool.__init__(self)
        self.outputfolder='Zreading'
        self.baseurl="http://www.zreading.cn/page/"
        self.pagerange=range(2,3)

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_menu(menuurl,page=None):#默认传URL，也可直接传网页内容进行测试
        soup = BeautifulSoup(page,from_encoding='utf8')
        indexbox=soup.find('div', { "id" : "content"})
        divlist=indexbox('h2',{"class":"entry-name"})
        articlelist=[item.find('a') for item in divlist]
        result=[]
        for item in articlelist:
            result.append(item["href"])
        return result

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_article(arturl,page=None):#默认传URL，也可直接传网页内容进行测试
        soup = BeautifulSoup(page,from_encoding='utf8')
        sp=soup.find('article',{"class":"entry-common"})
        title=sp.find('h2',{"class":"entry-name"}).string.strip()

        info=sp.find('div', {"class" : "entry-meta"})
        time=info.find('span', {"itemprop":"datePublished"}).string.strip()
        proplist=[item.string for item in info('a', { "rel" : "tag"})]
        if len(proplist)>1:
            catalog=proplist[0]
            keywords=",".join(proplist[1:])
        img=''

        content=sp.find('div',{"class":"entry-content"})
        content.contents.pop(0)#删除小标题
        innerlink=content.a
        # innerlink.extract()#删除文章内连接,有问题！

        #文章转成指定编码，默认为UTF8
        article=Bs4BaseTool.regx_article(str(content))

        art=NetArticle()
        art.url=arturl
        art.title=title
        art.posttime=time
        art.category=catalog
        art.keywords=keywords
        art.img=img
        art.article=unicode(article,code)
        return art    
        
def test_net():
    #在文件日志基础上，添加输出到控制台的日志
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s-%(levelname)s:%(message)s",datefmt='%d %b %Y,%H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # a=Time3Tool()#ZreadingTool
    a=ZreadingTool()
    logconfig(a.outputfolder)
    a.pagerange=range(1,30)
    a.parse_start()
    # a.parse_start_Thread()

def test_file():
    logconfig('test_file')
    # page=readfile(r'f:\test1.txt')
    # result=ZreadingTool.parse_menu('',page)
    # print result

    page=readfile(r'f:\test2.txt')
    result=ZreadingTool.parse_article('',page)
    print result
    print result.article.encode(code)
    result.make_article(u'f:/test_file')

if __name__ == '__main__':

    test_net()
    # test_file()

    

