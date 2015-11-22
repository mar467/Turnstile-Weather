# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 07:30:39 2015

@author: moizr_000
"""

from datetime import date, timedelta

class EasyDate(object):
    def __init__(self, datetime_date_obj):
        self.date = datetime_date_obj
        self.original_date = self.date
    
    # not a pointless getter function, because we're accessing an attribute's attribute  
    def get_day(self):
        return self.date.day
    def get_day_str(self):
        day = self.get_day()
        day_str = str(day)
        if day < 10:
            day_str = '0'+day_str
        return day_str
    def get_month(self):
        return self.date.month
    def get_month_str(self):
        month = self.get_month()
        month_str = str(month)
        if month < 10:
            month_str = '0'+month_str
        return month_str
    def get_year(self):
        return self.date.year
    def get_year_str(self):
        return str(self.get_year())
    def get_abbrev_year_str(self):
        return self.get_year_str()[-2:]
    def get_day_of_week(self): # 1 is Mon, 7 is Sun
        return self.date.isoweekday()

# MTA stands for Metro Transit Authority   
class MTAEasyDate(EasyDate):
    def __init__(self, datetime_date_obj):
        EasyDate.__init__(self, datetime_date_obj)
        self.make_this_Saturday()
        
    # MTA API only provides data on a weekly basis, corresponding to Saturday dates   
    def make_this_Saturday(self):
        days_to_add = 6 - self.get_day_of_week()
        if days_to_add == -1:
            days_to_add = 6
        delta_days = timedelta(days=days_to_add)
        self.date = self.date + delta_days
        return self
    def is_Saturday(self):
        return self.get_day_of_week() == 6
    def next_Saturday(self):
        next_Sat_date = self.date + timedelta(days=7)
        return MTAEasyDate(next_Sat_date) # automatically becomes Saturday (due to new make_this_Saturday call), even if self.is_Saturday is False
    def last_Saturday(self):
        last_Sat_date = self.date - timedelta(days=7)
        return MTAEasyDate(last_Sat_date)
        
# WU stands for Weather Underground
class WUEasyDate(EasyDate):
    def __init__(self, datetime_date_obj):
        EasyDate.__init__(self, datetime_date_obj)
       
    # WU API provides data on daily basis   
    def tomorrow(self):
        tomorrow_date = self.date + timedelta(days=1)
        return WUEasyDate(tomorrow_date)
    def yesterday(self):
        yesterday_date = self.date - timedelta(days=1)
        return WUEasyDate(yesterday_date)
    
class EasyDateList(object):
    def __init__(self, ezdate_min, ezdate_max): # takes in two date objects
        self.ezdate_min = ezdate_min
        self.ezdate_max = ezdate_max
        self.ezdate_list = [] # list of date objects
    
### since we will be using a range of dates, it will be useful 
### to make list of Saturday dates for subsequent indexing when extracting data
class MTAEasyDateList(EasyDateList):
    def __init__(self, ezdate_min, ezdate_max):
        EasyDateList.__init__(self, ezdate_min, ezdate_max)
        self.make_ezdate_list()
        
    def make_ezdate_list(self):
        mta_ezdate = MTAEasyDate(self.ezdate_min.date) # initializes to Saturday
        
        self.ezdate_list.append(mta_ezdate)
        
        while mta_ezdate.date < self.ezdate_max.date:
            mta_ezdate = mta_ezdate.next_Saturday()
            self.ezdate_list.append(mta_ezdate)
            
    def get_num_weeks(self):
        return len(self.ezdate_list)

        
class WUEasyDateList(EasyDateList):
    def __init__(self, ezdate_min, ezdate_max, start_yesterday=False):
        EasyDateList.__init__(self, ezdate_min, ezdate_max)
        self.make_ezdate_list(start_yesterday)

    def make_ezdate_list(self, start_yesterday):
        wu_ezdate = WUEasyDate(self.ezdate_min.date)
        
        # may be useful to start one day early to get 11:51 pm reading
        if start_yesterday:
           wu_ezdate = wu_ezdate.yesterday()
            
        self.ezdate_list.append(wu_ezdate)
        
        while wu_ezdate.date < self.ezdate_max.date - timedelta(days=1):
            wu_ezdate = wu_ezdate.tomorrow()
            self.ezdate_list.append(wu_ezdate)
            
    def get_num_days(self):
        return len(self.date_list)
        
        
'''
date_min = Date(10, 11, 2015)
date_max = Date(10, 31, 2015)

MTA_dates = MTADateList(date_min, date_max)
WU_dates = WUDateList(date_min, date_max)

MTA_dates.get_date_list()
WU_dates.get_date_list()
'''