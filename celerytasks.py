#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
import logging

from celery.task import task
from crawler import Crawler

@task
def crawler(url):
    Crawler(url).collect()
    return True
    
@task
def add_collect(book_id, chapter_idx, url):
    pass