# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 07:30:39 2015

@author: moizr_000
"""

from datetime import date, timedelta

class Date(object):
    def __init__(self, month, day, year):
        # month, day, year not included as attributes because liable to change frequently
        # instead, will use datetime.date objects
        self.date = self.make_date(month, day, year)
        self.original_date = self.date
        
    def make_date(self, month, day, year): 
        self.date = date(year, month, day)
    def get_day(self):
        return self.date.day
    def get_month(self):
        return self.date.month
    def get_year(self):
        return self.date.year
    def get_day_of_week(self): # 1 is Mon, 7 is Sun
        return self.date.isoweekday()

# MTA stands for Metro Transit Authority   
class MTADate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
        self.make_Saturday()
        
    # MTA API only provides data on a weekly basis, corresponding to Saturday dates   
    def make_Saturday(self):
        days_to_add = 6 - self.get_day_of_week()
        if days_to_add == -1:
            days_to_add = 6
        delta_days = timedelta(days=days_to_add)
        self.date = self.date + delta_days
    def is_Saturday(self):
        return self.get_day_of_week() == 6
    def make_next_Saturday(self):
        if not self.is_Saturday():
            self.make_Saturday()
        self.date = self.date + timedelta(days=7)
    def make_last_Saturday(self):
        if not self.isSaturday():
            self.make_Saturday()
        self.date = self.date - timedelta(days=7)
        
# WU stands for Weather Underground
class WUDate(Date):
    def __init__(self, month, day, year):
        Date.__init__(self, month, day, year)
       
    # WU API provides data on daily basis   
    def make_tomorrow(self):
        self.date + timedelta(days=1)
    def make_yesterday(self):
        self.date - timedelta(days=1)
    
class DateList(object):
    def __init__(self, date_min, date_max): # takes in two date objects
        self.date_min = date_min
        self.date_max = date_max
        self.date_list = [] # list of date objects
        
    def get_min_date(self): # NOT NECESSARY: no public/private in Python
        pass
    def get_max_date(self):  # NOT NECESSARY: no public/private in Python
        pass
    def get_date_list(self):  # NOT NECESSARY: no public/private in Python
        pass
    
### since we will be using a range of dates, it will be useful 
### to make list of Saturday dates for subsequent indexing when extracting data
class MTADateList(DateList):
    def __init__(self, date_min, date_max):
        DateList.__init__(self, date_min, date_max)
        mta_date = MTADate(self.date_min) # initializes to Saturday
        
        self.date_list.append(mta_date)
        
        while mta_date.date <= date_max.date:
            mta_date.make_next_Saturday()
            self.date_list.append(mta_date)
        
        self.num_weeks = len(self.date_list)
        
    def get_num_weeks(self): # NOT NECESSARY: no public/private in Python
        return self.num_weeks
        
def WUDateList(DateList):
    def __init__(self, date_min, date_max, start_yesterday=False):
        DateList.__init__(self, date_min, date_max)
        wu_date = WUDate(self.date_min)
        
        # may be useful to start one day early to get 11:51 pm reading
        if start_yesterday:
            wu_date.make_yesterday()
            
        self.date_list.append(wu_date)
        
        while wu_date.date <= date_max.date:
            wu_date.make_tomorrow()
            self.date_list.append(wu_date)
            
        self.num_days = len(self.date_list)
        
    def get_num_days(self): # NOT NECESSARY: no public/private in Python
        return self.num_days
        
'''
date_min = Date(10, 11, 2015)
date_max = Date(10, 31, 2015)

MTA_dates = MTADateList(date_min, date_max)
WU_dates = WUDateList(date_min, date_max)

MTA_dates.get_date_list()
WU_dates.get_date_list()
'''