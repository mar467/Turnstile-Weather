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
    def __init__(self, mta_ezdate):
        Link.__init__(self)
        self.ezdate = mta_ezdate
        self.make_url()
        
    def make_url(self):
        day = self.ezdate.get_day_str()
        month = self.ezdate.get_month_str()
        year = self.ezdate.get_abbrev_year_str()
        self.url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_"+year+month+day+".txt"
    
class WULink(Link):
    def __init__(self, wu_ezdate, location="KNYC"):
        Link.__init__(self)
        self.ezdate = wu_ezdate
        self.location = location
        self.make_url()
        
    def make_url(self):
        day = self.ezdate.get_day_str()
        month = self.ezdate.get_month_str()
        year = self.ezdate.get_year_str()
        self.url = "http://www.wunderground.com/history/airport/"+self.location+"/"+year+"/"+month+"/"+day+"/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10002&reqdb.magic=5&reqdb.wmo=99999&MR=1&format=1"

class LinkList(object): # NOT a link"ed" list, just a list of URL strings
    def __init__(self):
        self.url_list = []

        
class MTALinkList(LinkList):
    def __init__(self, mta_ezdate_list):
        LinkList.__init__(self)
        self.list_of_ezdates = mta_ezdate_list.ezdate_list
        self.make_url_list()
        
    def make_url_list(self):
        for ezdate in self.list_of_ezdates:
            self.url_list.append(MTALink(ezdate))
        
class WULinkList(LinkList):
    def __init__(self, wu_ezdate_list, location='KNYC'):
        LinkList.__init__(self)
        self.list_of_ezdates = wu_ezdate_list.ezdate_list
        self.location = location
        self.make_url_list()
        
    def make_url_list(self):
        for ezdate in self.list_of_ezdates:
            self.url_list.append(WULink(ezdate, self.location))
    