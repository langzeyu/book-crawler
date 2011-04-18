#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import datetime
import logging

from celery.task import task
from crawler import Crawler

@task
def add_crawler(url):
    
    Crawler(url).collect()
    return True
    
@task
def add_collect(url, file_name):
    pass