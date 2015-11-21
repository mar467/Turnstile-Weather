# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:31:18 2015

@author: moizr_000
"""

class EasyLink(object):
    def __init__(self):
        self.url = ""
        
class MTAEasyLink(EasyLink):
    def __init__(self, mta_ezdate):
        EasyLink.__init__(self)
        self.ezdate = mta_ezdate
        self.make_url()
        
    def make_url(self):
        day = self.ezdate.get_day_str()
        month = self.ezdate.get_month_str()
        year = self.ezdate.get_abbrev_year_str()
        self.url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_"+year+month+day+".txt"
    
class WUEasyLink(EasyLink):
    def __init__(self, wu_ezdate, location="KNYC"):
        EasyLink.__init__(self)
        self.ezdate = wu_ezdate
        self.location = location
        self.make_url()
        
    def make_url(self):
        day = self.ezdate.get_day_str()
        month = self.ezdate.get_month_str()
        year = self.ezdate.get_year_str()
        self.url = "http://www.wunderground.com/history/airport/"+self.location+"/"+year+"/"+month+"/"+day+"/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10002&reqdb.magic=5&reqdb.wmo=99999&MR=1&format=1"

class EasyLinkList(object): # NOT a link"ed" list, just a list of URL strings
    def __init__(self):
        self.ezlink_list = []

        
class MTAEasyLinkList(EasyLinkList):
    def __init__(self, mta_ezdate_list):
        EasyLinkList.__init__(self)
        self.list_of_ezdates = mta_ezdate_list.ezdate_list
        self.make_ezlink_list()
        
    def make_ezlink_list(self):
        for ezdate in self.list_of_ezdates:
            self.ezlink_list.append(MTAEasyLink(ezdate))
        
class WUEasyLinkList(EasyLinkList):
    def __init__(self, wu_ezdate_list, location='KNYC'):
        EasyLinkList.__init__(self)
        self.list_of_ezdates = wu_ezdate_list.ezdate_list
        self.location = location
        self.make_ezlink_list()
        
    def make_ezlink_list(self):
        for ezdate in self.list_of_ezdates:
            self.ezlink_list.append(WUEasyLink(ezdate, self.location))
    