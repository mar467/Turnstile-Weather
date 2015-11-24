# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:11:28 2015

@author: moizr_000
"""

import pandas as pd
from datetime import datetime, timedelta

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
        self.df['Subway Datetimes'] = pd.Series('', index=self.df.index)
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series["DATE"]+' '+data_series["TIME"]
            datetime_obj = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            self.df.loc[row_idx, 'Subway Datetimes'] = datetime_obj
        return self
    
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
        self.df['Weather Datetimes'] = pd.Series('', index=self.df.index)
        UTC_to_EDT_conversion = timedelta(hours = 4) # needed to convert supplied datetimes to EDT
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series['DateUTC<br />']
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S<br />")
            self.df.loc[row_idx, 'Weather Datetimes'] = datetime_obj - UTC_to_EDT_conversion
        return self
    
    def _clean_up(self):
        pass
    
    def find_closest_wu_datetime(datetime):
        pass
    
'''
Access csv_filepath of MasterFile written object via xxx.get_path()
'''