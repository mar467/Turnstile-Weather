# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 07:30:39 2015

@author: moizr_000
"""

class Date(object):
    def __init__(self, month, day, year):
        self.date = self.make_date(month, day, year)
        self.original_date = self.date
        
    def make_date(day, month, year): 
        pass
    def get_date(): 
        pass
    def get_day(): 
        pass
    def get_month():
        pass
    def get_year():
        pass

# MTA stands for Metro Transit Authority   
class MTADate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
        self.make_Saturday()
        
    # MTA API only provides data on a weekly basis, corresponding to Saturday dates   
    def make_Saturday():
        pass
    def make_next_Saturday():
        pass
    def make_last_Saturday():
        pass
        
# WU stands for Weather Underground
class WUDate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
       
    # WU API provides data on daily basis   
    def make_tomorrow():
        pass
    def make_yesterday():
        pass
    