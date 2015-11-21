# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:31:18 2015

@author: moizr_000
"""

import dates

class Link(object):
    def __init__(self):
        self.url = ""
        
class MTALink(Link):
    def __init__(self, mta_date):
        Link.__init__(self)
        self.date = mta_date
        self.make_url()
        
    def make_url(self):
        day = str(self.date.get_day())
        month = str(self.date.get_month())
        year = str(self.date.get_year())[2:]
        "http://web.mta.info/developers/data/nyct/turnstile/turnstile_1510"+str(day)+".txt"
        pass # will need to use subway_date.get_[day, month, year]()
    
class WULink(Link):
    def __init__(self, wu_date):
        Link.__init__(self)
        self.date = wu_date
        self.make_url()
        
    def make_url(self):
        pass

class LinkList(object): # NOT a link"ed" list, just a list of URL strings
    def __init__(self):
        self.url_list = []
        
    def get_url_list(self): # NOT NECESSARY: no public/private in Python
        return self.url_list
        
class MTALinkList(LinkList):
    def __init__(self, mta_date_list):
        LinkList.__init__(self)
        self.date_list = mta_date_list
        self.make_url_list()
        
    def make_url_list(self):
        pass # makes list of MTALink objects... calls on MTALink
        
class WULinkList(LinkList):
    def __init__(self, wu_date_list):
        LinkList.__init__(self)
        self.date_list = wu_date_list
        self.make_url_list()
        
    def make_url_list(self):
        pass
    