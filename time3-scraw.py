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
# import logging
global code
code='utf8'

class TimeArticle:
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

def readpage(pageurl):
    # proxy_support = urllib2.ProxyHandler({'http':'http://XX.XX.XX.XX:XXXX'})
    # opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
    # urllib2.install_opener(opener)
    content=""
    try:
        content= urllib2.urlopen(pageurl,timeout=5).read()  #important
    except Exception,e:
        print e
    return content

def parse_menu(menuurl,page=None):
    if page is None:
        page=readpage(menuurl)
        if page=="":
            return None

    soup = BeautifulSoup(page,from_encoding='utf8')
    indexbox=soup.find('div', { "class" : "indexbox_l"})
    divlist=indexbox('div',{"class":"left_contant"})
    articlelist=[item.findNext('a',target="_blank") for item in divlist]
    result=[]
    for item in articlelist:
        result.append(item["href"])
    return result
    
def parse_article(arturl,page=None):
    if page is None:
        page=readpage(arturl)
        if page=="":
            return None

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

    art=TimeArticle()
    art.url=arturl
    art.title=title
    art.posttime=time
    art.category=catalog
    art.keywords=keywords
    art.img=img
    art.article=unicode(article,code)
    return art

def make_desktop_path(foldername):
    path=r"c:"
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
    r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders',)
    path=unicode(_winreg.QueryValueEx(key, "Desktop")[0]+"\\Time3\\Page_%s"%foldername)

    if not os.path.exists(path):
        os.makedirs(path) #多重路径
    return path

def test_file():
    # filepath=r"f:\test.txt"
    filepath2=r"f:\test1.txt"
    # makebs(readfile(filepath))
    art=parse_article('file',readfile(filepath2))
    make_desktop_path()
    art.make_article()

def test_net():
    baseurl="http://www.timetimetime.net/catalog.asp?cate=2&page="
    pagerange=range(2,32)
    MyArt=[]
    menu_urllist=[["%s%s"%(baseurl,p),p] for p in pagerange]
    totallist=[]

    print "start...menu"

    for menu_url,pagename in menu_urllist:
        article_urllist=parse_menu(menu_url)
        if article_urllist is None:
            print "readmenupage Error:",menu_url
        elif len(article_urllist)>0:
            totallist.append([pagename,article_urllist])
        else:
            print "parse_menu Error:",menu_url

    print "start...page:%s"%len(totallist)        
    for i in xrange(len(totallist)):
        art=None
        pagename=totallist[i][0]
        article_urllist=totallist[i][1]
        folderpath=make_desktop_path(pagename)

        for j in xrange(len(article_urllist)):
            article_url=article_urllist[j]
            try:
                print article_url
                art= parse_article(article_url)
                print "ok"
                art.make_article(folderpath)
                print "ok2"
            except Exception,e:
                print e
    


if __name__ == '__main__':
    test_net()

    

