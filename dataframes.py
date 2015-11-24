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
        self.df['Subway Datetime'] = pd.Series('', index=self.df.index)
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series["DATE"]+' '+data_series["TIME"]
            datetime_obj = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            self.df.loc[row_idx, 'Subway Datetime'] = datetime_obj
        return self
    
    def _make_hourly_entries_col(self):
        hourly_entries = pd.Series(0, index=self.df.index)
        prev_entries = self.df.loc[0, 'ENTRIES'] # initialize prev_entries to first value in df['ENTRIES']
        prev_datetime = self.df.loc[0, 'Subway Datetime'] # same, for first datetime value
        for row_idx, data_series in self.df.iterrows():
            curr_entries = data_series['ENTRIES']
            curr_datetime = data_series['Subway Datetime']
            hours_elapsed = (curr_datetime - prev_datetime).total_seconds()/3600
            if hours_elapsed >= 0: # if still on same turnstile unit (datetimes are increasing)...
                delta_entries = curr_entries - prev_entries
                hourly_entries[row_idx] = delta_entries/hours_elapsed
            else: # if reached end of one turnstile unit, and on to other from start date again...
                hourly_entries[row_idx] = float('nan') # fill with averages afterwards?
            prev_entries = curr_entries
            prev_datetime = curr_datetime
        
        self.df['Entries Per Hour'] = hourly_entries
        return self.df
    
    def _make_hourly_exits_col(self):
        pass
    
    def _clean_up(self):
        pass
    
    def _fill_nan_with_averages(self):
        pass
    
class WUDataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self, csv_filepath)
        self._make_datetime_col()
        self._clean_up()
        
    def _make_datetime_col(self):
        self.df['Weather Datetime'] = pd.Series('', index=self.df.index)
        UTC_to_EDT_conversion = timedelta(hours = 4) # needed to convert supplied datetimes to EDT
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series['DateUTC<br />']
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S<br />")
            self.df.loc[row_idx, 'Weather Datetime'] = datetime_obj - UTC_to_EDT_conversion
        return self
    
    def _clean_up(self):
        pass
    
    def find_closest_wu_datetime(datetime):
        pass
    
'''
Access csv_filepath of MasterFile written object via xxx.get_path()
'''