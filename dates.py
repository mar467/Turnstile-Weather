# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 07:30:39 2015

@author: moizr_000
"""

class Date(object):
    def __init__(self, month, day, year):
        # month, day, year not included as attributes because liable to change frequently
        # instead, will use datetime objects
        self.date = self.make_date(month, day, year)
        self.original_date = self.date
        
    def make_date(day, month, year): 
        pass
    def get_date(self): 
        pass
    def get_day(self): 
        pass
    def get_month(self):
        pass
    def get_year(self):
        pass

# MTA stands for Metro Transit Authority   
class MTADate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
        self.make_Saturday()
        
    # MTA API only provides data on a weekly basis, corresponding to Saturday dates   
    def make_Saturday(self):
        pass
    def make_next_Saturday(self):
        pass
    def make_last_Saturday(self):
        pass
        
# WU stands for Weather Underground
class WUDate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
       
    # WU API provides data on daily basis   
    def make_tomorrow(self):
        pass
    def make_yesterday(self):
        pass
    
class DateList(object):
    def __init__(self, date_min, date_max): # takes in two date objects
        self.date_min = date_min
        self.date_max = date_max
        self.date_list = [] # list of date objects
        
    def get_min_date(self):
        pass
    def get_max_date(self):
        pass
    def get_date_list(self):
        pass
    
### since we will be using a range of dates, it will be useful 
### to make list of Saturday dates for subsequent indexing when extracting data
class MTADateList(DateList):
    def __init__(self, date_min, date_max):
        DateList.__init__(self, date_min, date_max)
        mta_date = MTADate(self.date_min) # initializes to Saturday
        
        self.date_list.append(mta_date)
        
        while mta_date.get_date() <= date_max.get_date():
            mta_date.make_next_Saturday()
            self.date_list.append(mta_date)
        
        self.num_weeks = len(self.date_list)
        
    def get_num_weeks(self):
        return self.num_weeks