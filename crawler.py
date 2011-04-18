#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import hashlib
import urllib2
import urlparse
import zipfile
import logging

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

from tornado import template
from BeautifulSoup import BeautifulSoup
from scrapy.selector import HtmlXPathSelector

from rules import rules

import encodings
encodings.aliases.aliases['gb2312'] = 'gb18030'
encodings.aliases.aliases['gbk'] 	= 'gb18030'

user_agent = "Mozilla/5.0 (Linux; U; en-US) AppleWebKit/528.5+ (KHTML, like Gecko, Safari/538.5+) Version/4.0 Kindle/3.0 (screen 600x800; rotate)"

tpl_dir  = os.path.join(os.path.dirname(__file__), 'tpl')
data_dir = os.path.join(os.path.dirname(__file__), 'data')
kindlegen = os.path.join(os.path.dirname(__file__), 'lib', 'kindlegen')

class Book(object):
    """docstring for Book"""
    
    id = ""
    name = ""
    author = ''
    chapter_list = []
    
    source = ""
    book_dir = ""
    chapters_dir = ""
    
    index = 1
    
    def __init__(self, source=None, id=None):
        
        if id is None:
            self.id = hashlib.sha1(source).hexdigest()
        else:
            self.id = id
        
        self.source = source
        self.book_dir = os.path.join(data_dir, self.id)
        self.chapters_dir = os.path.join(self.book_dir, 'chapters')
        
        if os.path.isfile(os.path.join(self.book_dir, 'bookname')):
            fp = open(os.path.join(self.book_dir, 'bookname'), 'r')
            self.name = fp.read()
            fp.close()
        
    def init(self):
        """docstring for init"""
        if os.path.isdir(self.book_dir) is False:
            os.mkdir(self.book_dir)
        
        if os.path.isdir(self.chapters_dir) is False:
            os.mkdir(self.chapters_dir)
    
    def lock(self):
        """docstring for lock"""
        
        fp = open(os.path.join(self.book_dir, 'lock'), 'w')
        fp.write('lock')
        fp.close()
        
    def unlock(self):
        """docstring for unlick"""
        os.unlink(os.path.join(self.book_dir, 'lock'))
    
    def set_name(self, name):
        self.name = name
        fp = open(os.path.join(self.book_dir, 'bookname'), 'w')
        fp.write(name)
        fp.close()
        
    @property
    def is_lock(self):
        """docstring for is_lock"""
        return os.path.isfile(os.path.join(self.book_dir, 'lock'))
    
    @property
    def is_exists(self):
        """docstring for exits"""
        return os.path.isdir(self.book_dir)
        
    @property
    def is_ready(self):
        
        print os.path.join(self.book_dir, "book.mobi")
        print os.path.join(self.book_dir, "book.epub")
        if os.path.isfile(os.path.join(self.book_dir, "book.mobi")) \
            and os.path.isfile(os.path.join(self.book_dir, "book.epub")):
            return True
        else:
            return False
    
    @property
    def mobi(self):
        mobi = os.path.join(self.book_dir, "book.mobi")
        
        if os.path.isfile(mobi):
            return os.path.join(self.book_dir, "book.mobi") #"%s/book.mobi" % self.id
        else:
            return None
    
    @property
    def epub(self):
        """docstring for get_epub"""
        
        epub = os.path.join(self.book_dir, "book.epub")
        if os.path.isfile(epub):
            return os.path.join(self.book_dir, "book.epub") #"%s/book.epub" % self.id
        else:
            return None

    def add_chapter(self, title, content, source=None, index=None):
        """docstring for fname"""
        
        if index is None:
            index = self.index
            self.index += 1
            
        file_name = "chapter_%04d.html" % index
        self.render("chapter.html", os.path.join(self.chapters_dir, file_name), title=title, content=content)

        self.chapter_list.append({
            'index': index,
            'title': title,
            'file': file_name
        })
        
    def collect(self):
        pass
        
    def create(self):
        """docstring for create_index"""
        self.render("toc.html", os.path.join(self.book_dir, "toc.html"), title=self.name, chapters=self.chapter_list)
        self.render("toc.ncx", os.path.join(self.book_dir, "toc.ncx"), title=self.name, chapters=self.chapter_list)
        self.render("content.opf", os.path.join(self.book_dir, "content.opf"), title=self.name, author=self.author, chapters=self.chapter_list)
        self.render("cover.html", os.path.join(self.book_dir, "cover.html"), title=self.name, author=self.author)
        self.render("style.css", os.path.join(self.book_dir, "style.css"))
    
    def render(self, tpl_name, file_name, **kargs):
        """docstring for render"""
        content = self.render_string(tpl_name, source_hash=self.source_hash, **kargs)
        
        fp = open(file_name, 'w')
        fp.write(content)
        fp.close()
        
    def render_string(self, tpl_name, **kargs):
        """docstring for render_string"""
        return template.Loader(tpl_dir).load(tpl_name).generate(**kargs)
      
    def toEpub(self):
        """docstring for toEpub"""

        epub_file = os.path.join(self.book_dir, "book.epub")

        zip = zipfile.ZipFile(epub_file, mode='w', compression=zipfile.ZIP_DEFLATED)
        
        zip.write(os.path.join(tpl_dir, 'mimetype'), 'mimetype', zipfile.ZIP_STORED)
        zip.write(os.path.join(tpl_dir, 'META-INF', 'container.xml'), 'META-INF/container.xml')
        zip.write(os.path.join(tpl_dir, 'style.css'), "style.css")
        zip.write(os.path.join(self.book_dir, 'content.opf'), "content.opf")
        zip.write(os.path.join(self.book_dir, 'cover.html'), "cover.html")
        zip.write(os.path.join(self.book_dir, 'toc.html'), "toc.html")
        zip.write(os.path.join(self.book_dir, 'toc.ncx'), "toc.ncx")
        
        for chapter in self.chapter_list:
            zip.write(os.path.join(self.chapters_dir, chapter['file']), "chapters/%s" % chapter['file'])
            
        zip.close()

    def toPdf(self):
        """docstring for toPdf"""
        pass
    
    def toMobi(self):
        """docstring for toMobi"""
        os.system('%s %s -o "%s"' % (kindlegen, os.path.join(self.book_dir, "content.opf"), "book.mobi"))

class Crawler(object):
    """docstring for Crawler"""
    
    remove_tags = ['script','object','video','embed','iframe','noscript','style','img']
    remove_attrs = ['title','width','height','onclick','onload']
    
    def __init__(self, url):
        
        self.url = url
        
    def run(self):
        """docstring for run"""
        
        book = Book(self.url)
        
        if book.is_lock:
            logging.info("book is queueing")
            return
        else:
             book.lock()
             book.init()
        
        url_obj = urlparse.urlparse(self.url)
        
        if url_obj.hostname in rules:
            rule = rules[url_obj.hostname]
        else:
            logging.error("rule not found!")
            return
        
        logging.debug("start collect index...")
        html =  self.get_contents(self.url)
        
        if html is None:
            logging.error("can't conntect %s " % self.url)
            return
        
        soup = BeautifulSoup(html)
        html = soup.renderContents('utf-8')
        
        hxs = HtmlXPathSelector(text=html)
        
        book.set_name(hxs.select(rule['book_name']).extract()[0].strip())
        book.author = hxs.select(rule['book_author']).extract()[0].strip()
        
        chapter_list =  hxs.select(rule['chapter_list']).extract()
        

        logging.debug("start collect chapters...")
        i = 0
        for chapter in chapter_list:
            subsoup = BeautifulSoup(chapter)
            
            a = subsoup.find('a')
            # print a['href'], a.contents[0]
            
            chapter_url = urlparse.urljoin(self.url, a['href'])
            
            chapter_content = self.get_contents(chapter_url)
            
            if chapter_content is None:
                continue
            
            subsoup = BeautifulSoup(chapter_content)
            chapter_content = subsoup.renderContents('utf-8')

            hxs = HtmlXPathSelector(text=chapter_content)
            
            chapter_content = hxs.select(rule['chapter_content']).extract()[0].strip()
            
            subsoup = BeautifulSoup(chapter_content)
            
            for tag in subsoup.findAll(self.remove_tags):
                tag.extract()
                
            for tag in list(subsoup.findAll(attrs={"style":"display:none"})):
                tag.extract()
            
            book.add_chapter(a.contents[0], subsoup.renderContents('utf-8'))
        
        logging.debug("start building...")
        
        book.create()
        book.toEpub()
        book.toMobi()
        book.unlock()

    def get_contents(self, url, referer=None):
        """docstring for get_romte"""

        try:
            req = urllib2.Request(url)
            req.add_header('User-Agent', user_agent)

            if referer is not None:
                req.add_header('Referer', referer)

            response = urllib2.urlopen(req)
            data = response.read()

            response.close()
            response = None
            del response
            return data
        except Exception, e:
            logging.error("collect %s filed!" % url)
            return None

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(msecs)03d %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')
    Crawler("http://www.21shu.com/Html/Book/3/3310/").run()
        