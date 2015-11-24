# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:11:28 2015

@author: moizr_000
"""

import pandas as pd

class DataFrame(object):
    def __init__(self, csv_filepath):
        self.df = pd.read_csv(csv_filepath)
        
class MTADataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self, csv_filepath)
        self._make_datetime_col()
        self._make_hourly_entries_col()
        self._make_hourly_exits_col()
        self._clean_up()
        
    def _make_datetime_col(self):
        pass
    
    def _make_hourly_entries_col(self):
        pass
    
    def _make_hourly_exits_col(self):
        pass
    
    def _clean_up(self):
        pass
    
class WUDataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self, csv_filepath)
        self._make_datetime_col()
        self._clean_up()
        
    def _make_datetime_col(self):
        pass
    
    def _clean_up(self):
        pass
    
    def find_closest_wu_datetime(datetime):
        pass
    
'''
Access csv_filepath of MasterFile written object via xxx.get_path()
'''