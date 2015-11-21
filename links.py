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
        day = self.date.get_day_str()
        month = self.date.get_month_str()
        year = self.date.get_abbrev_year_str()
        self.url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_"+year+month+day+".txt"
    
class WULink(Link):
    def __init__(self, wu_date, location="KNYC"):
        Link.__init__(self)
        self.date = wu_date
        self.location = location
        self.make_url()
        
    def make_url(self):
        day = self.date.get_day_str()
        month = self.date.get_month_str()
        year = self.date.get_year_str()
        self.url = "http://www.wunderground.com/history/airport/"+self.location+"/"+year+"/"+month+"/"+day+"/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10002&reqdb.magic=5&reqdb.wmo=99999&MR=1&format=1"

class LinkList(object): # NOT a link"ed" list, just a list of URL strings
    def __init__(self):
        self.url_list = []

        
class MTALinkList(LinkList):
    def __init__(self, mta_date_list):
        LinkList.__init__(self)
        self.date_list = mta_date_list
        self.make_url_list()
        
    def make_url_list(self):
        for date in self.date_list:
            self.url_list.append(MTALink(date))
        
class WULinkList(LinkList):
    def __init__(self, wu_date_list, location='KNYC'):
        LinkList.__init__(self)
        self.date_list = wu_date_list
        self.location = location
        self.make_url_list()
        
    def make_url_list(self):
        for date in self.date_list:
            self.url_list.append(WULink(date, self.location))
    