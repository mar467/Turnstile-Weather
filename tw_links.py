# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:31:18 2015

@author: moizr_000
"""

'''
The purpose of the following classes is to construct a list of URL links for
Metro Transit Authority data and Weather Underground data using the 
EasyDateList classes from the tw_dates module (hence the retaining of the 
"Easy" terminology).
'''

class EasyLink(object):
    def __init__(self):
        self.url = ""
        
class MTAEasyLink(EasyLink):
    def __init__(self, mta_ezdate):
        EasyLink.__init__(self)
        self._ezdate = mta_ezdate
        self._make_url()
        
    def _make_url(self):
        day = self._ezdate.get_day_str()
        month = self._ezdate.get_month_str()
        year = self._ezdate.get_abbrev_year_str()
        self.url = "http://web.mta.info/developers/data/nyct/turnstile/turnstile_"+year+month+day+".txt"
        return self        
        
class WUEasyLink(EasyLink):
    def __init__(self, wu_ezdate, location="KNYC"):
        EasyLink.__init__(self)
        self._ezdate = wu_ezdate
        self._location = location
        self._make_url()
        
    def _make_url(self):
        day = self._ezdate.get_day_str()
        month = self._ezdate.get_month_str()
        year = self._ezdate.get_year_str()
        self.url = "http://www.wunderground.com/history/airport/"+self._location+"/"+year+"/"+month+"/"+day+"/DailyHistory.html?req_city=New+York&req_state=NY&req_statename=New+York&reqdb.zip=10002&reqdb.magic=5&reqdb.wmo=99999&MR=1&format=1"
        return self

class EasyLinkList(object): # NOT a link"ed" list, just a list of URL strings
    def __init__(self):
        self.ezlink_list = []

class MTAEasyLinkList(EasyLinkList):
    def __init__(self, mta_ezdate_list):
        EasyLinkList.__init__(self)
        self._list_of_ezdates = mta_ezdate_list.ezdate_list
        self._make_ezlink_list()
        
    def _make_ezlink_list(self):
        for ezdate in self._list_of_ezdates:
            self.ezlink_list.append(MTAEasyLink(ezdate))
        return self
        
class WUEasyLinkList(EasyLinkList):
    def __init__(self, wu_ezdate_list, location='KNYC'):
        EasyLinkList.__init__(self)
        self._list_of_ezdates = wu_ezdate_list.ezdate_list
        self._location = location
        self._make_ezlink_list()
        
    def _make_ezlink_list(self):
        for ezdate in self._list_of_ezdates:
            self.ezlink_list.append(WUEasyLink(ezdate, self._location))
        return self