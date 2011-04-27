#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import division
import os
import logging
import time
import hashlib
import urlparse
import re
from datetime import datetime, timedelta
from urllib import unquote, quote_plus

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options

try:
    import daemon
except:
    daemon = None

from crawler import Book
from rules import *

import celerytasks

define("port", default=8800, help="The port to be listened", type=int)
define("daemon", default=False, help="daemon mode", type=bool)
define("debug", default=False, help="debug mode", type=bool)

data_dir = os.path.join(os.path.dirname(__file__), 'data')

class Application(tornado.web.Application):
    def __init__(self):
        urls = [
            (r"/", HomeHandler),
            (r"/book/([a-z0-9]+)", BookHandler),
            (r"/book/([a-z0-9]+).(epub|mobi)", DownHandler),
        ]
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__), "views"),
            static_path = os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies = True,
            cookie_secret = "kL5gEmGeJJFuYh711oETzKXQAGaYdEQnp2XdTP1o/Vo=",
            debug = options.debug,
            login_url = "/login",
        )
        tornado.web.Application.__init__(self, urls, **settings)
        
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s:%(msecs)03d %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M', filename= os.path.join(os.path.dirname(__file__), "logs", "website.log"), filemode='a')
        
class BaseHandler(tornado.web.RequestHandler):

    def is_url(self, text):
        """docstring for is_url"""
        return text.partition("://")[0] in ('http', 'https')
    
    def in_rules(self, url):
        """docstring for in_rules"""
        
        url = urlparse.urlparse(url)
        
        return url.hostname in Rules
        
    def url_validate(self, url):
        """docstring for validate"""
        url = urlparse.urlparse(url)
        rule = Rules[url.hostname]
        
        if 'url_validate' in rule and not re.match(rule['url_validate'], url):
            return False
        else:
            return True

class HomeHandler(BaseHandler):
    """docstring for HomeHandler"""
    def get(self, error=None, url=None, book_id=None):
        """docstring for fname"""
        
        if url is None:
            url = self.get_argument("url", None)
        
        allow_sites = Rules.keys()
        
        self.render("home.html", error = error, url=url, book_id=book_id, allow_sites=allow_sites)
        
        
    def post(self):
        """docstring for fname"""
        
        url = self.get_argument("url", None)
        
        if not url:
            self.get(2, url)
        elif not self.is_url(url):
            self.get(3, url)
        elif not self.in_rules(url):
            self.get(4, url)
        elif not self.url_validate(url):
            self.get(5, url)
        else:
            
            book = Book(url)
            if not book.is_exists:
                celerytasks.crawler.apply_async(args=[url]) #, eta=datetime.now() + timedelta(seconds=10))
                
            self.redirect('book/%s' % book.id)
            
class BookHandler(BaseHandler):
    """docstring for BookHandler"""
    
    def get(self, book_id):
        """docstring for get"""
        
        book = Book(id=book_id)
        self.render('down.html', book=book)
    
class DownHandler(BaseHandler):
    """docstring for DownHandler"""
    
    def get(self, book_id, filetype):
        
        mime_types = {
            'mobi':'application/x-mobipocket-ebook',
            'epub':'application/epub-zip'
        }
        
        book = Book(id=book_id)
        
        if filetype is 'epub':
            book_file = book.epub
        else:
            book_file = book.mobi
            
        fp = open(book_file, 'r')
        data = fp.read()
        fp.close()
        
        self.set_header("Content-Type", mime_types[filetype])
        self.set_header("Content-Length", len(data))
        self.set_header("Content-Disposition", 'attachment; filename="%s.%s"' % (book.id, filetype))
        self.set_header("Cache-Control", "private, max-age=0, must-revalidate")
        self.set_header("Pragma", "public")
        self.write(data)

def runserver():
    tornado.options.parse_command_line()
    
    if options.daemon and daemon:
        log = open(os.path.join(os.path.dirname(__file__), 'logs', 'website%s.log' % options.port), 'a+')
        ctx = daemon.DaemonContext(stdout=log, stderr=log,  working_directory='.')
        ctx.open()
    
    http_server = tornado.httpserver.HTTPServer(Application())
    
    if options.debug:
        http_server.listen(options.port)
    else:
        http_server.bind(options.port)
        http_server.start(4)

    tornado.ioloop.IOLoop.instance().start()
    
if __name__ == "__main__":
    runserver()