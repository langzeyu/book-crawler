#!/usr/bin/env python
# encoding: utf-8
"""
rules.py

Created by Jerry on 2011-04-18.
Copyright (c) 2011 __MyCompanyName__. All rights reserved.
"""

Rules = {}

Rules['www.21shu.com'] = {
    'book_name': "//div[@id='TextTitle']/span[@class='booktitle']/text()",
    'book_author': '/html/body/center/div/div[2]/div[2]/a/text()',
    'chapter_list': "/html/body/center/div/div[2]/div[3]/ul[2]/*/a",
    'chapter_title': "//div[@id='TextTitle']/span[@class='booktitle']/text()",
    'chapter_content': "//div[@id='BookText']",
}

