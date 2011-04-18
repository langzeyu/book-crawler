"""
XPath selectors

Two backends are currently available: libxml2 and lxml

To select the backend explicitly use the SELECTORS_BACKEND variable in your
project. Otherwise, libxml2 will be tried first. If libxml2 is not available,
lxml will be used.
"""

from scrapy.selector.libxml2sel import *