# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 07:30:39 2015

@author: moizr_000
"""

'''
The purpose of the following classes is to make obtaining a list of URL links
for Metro Transit Authority data and Weather Underground data corresponding to
a range of dates a straightforward process. Among things considered was that
MTA data was provided on a weekly basis by Saturdays, with the week 
corresponding to the seven days before that Saturday (not including that
Satuday itself), whereas WU data was provided on a daily basis from 12:51 am
to 11:51 pm. 

The use of the "EasyDate" terminology was to avoid confusion with
the "Date" class from the datetime module.
'''

from datetime import date, timedelta

class Date(object): # responsibility: for Link classes
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
        
class EasyDate(Date): # responsibility: for child classes, and EasyDateList classes
    def __init__(self, datetime_date_obj):
        Date.__init__(self, datetime_date_obj)
        
    # the following "get" methods all return datetime objects
    def get_tomorrow(self): 
        return self.date + timedelta(days=1)
    def get_yesterday(self):
        return self.date - timedelta(days=1)
    def get_next_week(self):
        return self.date + timedelta(days=7)
    def get_last_week(self):
        return self.date - timedelta(days=7)
    def get_this_Saturday(self):
        days_to_add = 6 - self.get_day_of_week()
        if days_to_add == -1:
            days_to_add = 6
        delta_days = timedelta(days=days_to_add)
        return self.date + delta_days
    def get_last_Saturday(self):
        return self.get_this_Saturday() - timedelta(days=7) # lazy
    def is_Saturday(self):
        return self.get_day_of_week() == 6
        
    '''
    def this_Saturday(self): # returns new EasyDate object
        return EasyDate(self.get_this_Saturday())
    def last_Saturday(self): # returns new EasyDate object
        return EasyDate(self.get_last_Saturday())
    '''

# MTA stands for Metro Transit Authority   
class MTAEasyDate(EasyDate):
    def __init__(self, datetime_date_obj):
        EasyDate.__init__(self, datetime_date_obj)
        self._make_this_Saturday() # MTA API only provides data on a weekly basis, corresponding to Saturday dates   
        
    def _make_this_Saturday(self):
        self.date = self.get_this_Saturday()
        return self
    
    def next_Saturday(self): # returns new MTAEasyDate object
        return MTAEasyDate(self.get_next_week()) # automatically initialized to Saturday
        
# WU stands for Weather Underground
class WUEasyDate(EasyDate):
    def __init__(self, datetime_date_obj):
        EasyDate.__init__(self, datetime_date_obj) # WU API provides data on daily basis  
        
    def tomorrow(self): # returns new WUEasyDate object
        return WUEasyDate(self.get_tomorrow())
        
    def yesterday(self): # returns new WUEasyDate object
        return WUEasyDate(self.get_yesterday())
    
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
        self._make_ezdate_list()
        
    def _make_ezdate_list(self):
        mta_ezdate = MTAEasyDate(self.ezdate_min.date) # initializes to Saturday
        
        self.ezdate_list.append(mta_ezdate)
        
        while mta_ezdate.date < self.ezdate_max.date:
            mta_ezdate = mta_ezdate.next_Saturday()
            self.ezdate_list.append(mta_ezdate)
            
        return self
            
    def get_num_weeks(self):
        return len(self.ezdate_list)

        
class WUEasyDateList(EasyDateList):
    def __init__(self, ezdate_min, ezdate_max, start_yesterday=False):
        EasyDateList.__init__(self, ezdate_min, ezdate_max)
        self.ezdate_min = self.ezdate_min
        self._make_ezdate_list(start_yesterday)

    def _make_ezdate_list(self, start_yesterday):
        wu_ezdate = WUEasyDate(self.ezdate_min.get_last_Saturday())
        
        # may be useful to start one day early to get 11:51 pm reading
        if start_yesterday:
           wu_ezdate = wu_ezdate.yesterday()
            
        self.ezdate_list.append(wu_ezdate)
        
        while wu_ezdate.date < self.ezdate_max.get_this_Saturday() - timedelta(days=1):
            wu_ezdate = wu_ezdate.tomorrow()
            self.ezdate_list.append(wu_ezdate)
            
        return self
            
    def get_num_days(self):
        return len(self.date_list)