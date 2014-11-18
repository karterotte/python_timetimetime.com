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
        return "%s\t%s"%(self.title.encode(code),self.keywords.encode(code))

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
    try:
        content= urllib2.urlopen(pageurl,timeout=5).read()  #important
    except Exception,e:
        print e
        logging.error("readpage Error:"+pageurl)
    return content

class Bs4BaseTool:
    def __init__(self):
        self.menu_urllist = []
        self.outputfolder='MyArt'
        self.totallist=[]
        self.baseurl=''
        self.pagerange=range(1,2)
        logging.basicConfig(filename='%s-log.txt'%self.outputfolder,\
            level=logging.INFO,format="%(asctime)s-%(levelname)s:%(message)s",datefmt='%d %b %Y,%H:%M:%S')

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
        return menu_urllist

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_menu(menuurl,page=None):
        article_urllist=[]
        #override
        return article_urllist

    @staticmethod
    @timeused_deco
    @readpage_deco
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
    def parse_start(self):
        self.totallist=[]
        self.menu_urllist=[]
        self.menu_urllist=self.make_menulist()

        print "start...menu"
        for menu_url,pagename in self.menu_urllist:
            article_urllist=self.parse_menu(menu_url,None)
            if article_urllist is None:
                print "read_menupage Error:",menu_url
                logging.error("read_menupage Error:"+menu_url)
            elif len(article_urllist)>0:
                self.totallist.append([pagename,article_urllist])
            else:
                print "parse_menu Error:",menu_url
                logging.error("parse_menu Error:"+menu_url)

        print "start...page:%s"%len(self.totallist)        
        for i in xrange(len(self.totallist)):
            art=None
            pagename=self.totallist[i][0]
            article_urllist=self.totallist[i][1]
            folderpath=self.make_desktop_path(pagename)

            for j in xrange(len(article_urllist)):
                article_url=article_urllist[j]
                try:
                    art= self.parse_article(article_url,None)
                    art.make_article(folderpath)
                    logging.info("make_article OK:"+art.title)
                except Exception,e:
                    print e
                    logging.error("parse_article Error:"+article_url)
        
class Time3Tool(Bs4BaseTool):
    """timetimetime.com"""
    def __init__(self):
        Bs4BaseTool.__init__(self)
        self.outputfolder='Time3'
        self.baseurl="http://www.timetimetime.net/catalog.asp?cate=2&page="
        self.pagerange=range(1,2)

    def make_menulist(self):
        menu_urllist=[]
        menu_urllist=[["%s%s"%(self.baseurl,p),p] for p in self.pagerange]
        return menu_urllist

    @staticmethod
    @timeused_deco
    @readpage_deco
    def parse_menu(menuurl,page=None):
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
    def parse_article(arturl,page=None):
        soup = BeautifulSoup(page,from_encoding='utf8')
        title=soup.find('title').string.split('|')[0].strip()
        keywords=soup.find('meta',{"name":"keywords"})["content"]
        indexbox=soup.find('div', { "class" : "indexbox_l"})
        info=indexbox.find('div',{"class":"neirongxinxi a9"})
        content=indexbox.find('div',{"class":"neiz1 a7"})
        time=info.find('a',href="#").string
        catalog=info.find('a',title=True).string
        # keywords=",".join([item.string for item in info('a', { "class" : "tags"})])
        img=content.find('img')["src"]
        content.contents.pop(0)
        from regtest import regx_article
        article=regx_article(content.renderContents())

        # print '\r\n'.join([item.string for item in content.contents])
        # for index,item in enumerate(content.contents):
        #     print item 

        # article="\r\n\r\n".join(["     "+item.string.replace('\n','') for item in content('p')])

        art=NetArticle()
        art.url=arturl
        art.title=title
        art.posttime=time
        art.category=catalog
        art.keywords=keywords
        art.img=img
        art.article=unicode(article,code)
        return art


def test_file():
    # filepath=r"f:\test.txt"
    filepath2=r"f:\test1.txt"
    # makebs(readfile(filepath))
    art=parse_article_Time3('file',readfile(filepath2))
    make_desktop_path()
    art.make_article()

def test_net():
    a=Time3Tool()
    a.pagerange=range(1,3)
    a.parse_start()

if __name__ == '__main__':
    test_net()

    

