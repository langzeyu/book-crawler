#!/usr/bin/env python
# encoding: utf-8
"""
rules.py

Created by Jerry on 2011-04-18.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

Rules = {}

Rules['www.21shu.com'] = {
    'encoding': "gb2312",
    'url_validate' : r'^http:\/\/www\.21shu\.com\/Html\/Book\/[0-9]+\/[0-9]+\/(index\.html)?$',
    'book_name': "//div[@id='TextTitle']/span[@class='booktitle']/text()",
    'book_author': "//div[@id='TextInfo']/a/text()",
    'chapter_list': "//div[@id='BookText']/ul/li/a",
    'chapter_title': "//div[@id='TextTitle']/span[@class='newstitle']/text()",
    'chapter_content': "//div[@id='BookText']",
}

def dangdang_id(url):
    url = url.split('_')
    return url[1]

Rules['read.dangdang.com'] = {
    'encoding': 'gbk',
    'url_validate' : r'^http:\/\/read\.dangdang\.com\/book_[0-9]+.*$',
    'book_name': "//div[@class='book_title works_title']/h1/text()",
    'book_author': "//div[@class='buy_detail']/div[@class='deta_1']/p/a/text()",
    'book_cover': "//div[@class='pic_bg_f']/span/img/@src",
    'book_id': dangdang_id,
    'chapter_url':'http://read.dangdang.com/book_chapter_list.php?book_id=%s',
    'chapter_list': "//div[@id='__zhangjie']//a",
    'chapter_title': "//div[@class='cont_detail']/h2/text()",
    'chapter_content': "//div[@id='content']",
}

def qidian_filter(content):
    """docstring for qidain_filter"""
    content = content[16:]
    content = content[:-6]
    content = content.replace("<p>　　", "<p>")
    return content

Rules['www.qidian.com'] = {
    'encoding': 'gb2312',
    'url_validate' : r'^http:\/\/www\.qidian\.com\/BookReader\/[0-9]+\.aspx$',
    'book_name': "//div[@class='booktitle']/h1/text()",
    'book_author': "//div[@id='bookdirectory']/div/div[@class='booktitle']/span/a[1]/text()",
    'chapter_list': "//div[@id='content']/div[@class='box_cont']/div[@class='list']//a",
    'chapter_title': "//span[@id='lbChapterName']/text()",
    'chapter_content_url': "//div[@id='content']/script/@src",
    'chapter_content_filter': qidian_filter,
}

Rules['read.360buy.com'] = {
    'encoding': "gb2312",
    'url_validate' : r'^http:\/\/read\.360buy\.com\/[0-9]+\/(index\.html)?$',
    'book_name': "//div[@class='m works']/div[@class='mt']/h3/text()[2]",
    'book_author': "//div[@class='book-authorinfo']/a[1]/text()",
    'book_cover': "//div[@id='book-cover']/a/img/@src",
    'chapter_list': "//div[@class='books-list clearfix']/ul//a",
    'chapter_title': "//div[@id='information']/div[@class='mc clearfix']/h1/text()",
    'chapter_content': "//div[@id='zoom']",
}