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
        self._clean_up()
        self._make_datetime_col()
        self._make_hourly_entries_col()
        self._make_hourly_exits_col()
        self._delete_unneeded_cols()
        
    def _clean_up(self):
        new_columns = []
        for i in range(len(self.df.columns)):
            new_columns.append(self.df.columns[i].strip().title())
        self.df.columns = new_columns
        return self

    def _make_datetime_col(self):
        self.df['Subway Datetime'] = pd.Series('', index=self.df.index)
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series["Date"]+' '+data_series["Time"]
            datetime_obj = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M:%S')
            self.df.loc[row_idx, 'Subway Datetime'] = datetime_obj
        return self
    
    def _make_hourly_entries_col(self):
        hourly_entries = pd.Series(0, index=self.df.index)
        prev_entries = self.df.loc[0, 'Entries'] # initialize prev_entries to first value in df['ENTRIES']
        prev_datetime = self.df.loc[0, 'Subway Datetime'] # same, for first datetime value
        for row_idx, data_series in self.df.iterrows():
            curr_entries = data_series['Entries']
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
        return self
    
    def _make_hourly_exits_col(self):
        hourly_exits = pd.Series(0, index=self.df.index)
        prev_exits = self.df.loc[0, 'Exits']
        prev_datetime = self.df.loc[0, 'Subway Datetime']
        for row_idx, data_series in self.df.iterrows():
            curr_exits = data_series['Exits']
            curr_datetime = data_series['Subway Datetime']
            hours_elapsed = (curr_datetime - prev_datetime).total_seconds()/3600
            if hours_elapsed >= 0:
                delta_exits = curr_exits - prev_exits
                hourly_exits[row_idx] = delta_exits/hours_elapsed
            else:
                hourly_exits[row_idx] = float('nan')
            prev_exits = curr_exits
            prev_datetime = curr_datetime
            
        self.df['Exits Per Hour'] = hourly_exits
        return self
        
    def _delete_unneeded_cols(self):
        self.df = self.df.drop(['Date', 'Time'], 1)
        return self
    
    def _fill_nan_with_averages(self):
        pass
    
class WUDataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self, csv_filepath)
        self._clean_up()
        self._make_datetime_col()
        self._delete_unneeded_cols()
        
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
    
    def _delete_unneeded_cols(self):
        self.df = self.df.drop(['DateUTC<br />', 'TimeEDT'], 1)
        return self
    
    # efficient method of finding closest datetime that does not require searching through all weather datetimes
    def find_closest_wu_datetime(self, datetime_obj):
        ''' 
        The strategy here will be keep calculating the difference between the datetime_obj and the datetimes
        in the weather dataframe... WHILE the differences are decreasing (i.e.: approaching a local minima).
        So as soon as the differences start to INCREASE (just passing minima), return the previous index as
        the closest match. This works because the datetimes in the weather dataframe will always be in increasing
        descending order. If the datetime_obj is earlier than any weather date, the first index will be returned,
        and if the datetime_obj is later than any weather date, the last index will be returned.
        '''
        # initialize with largest possible difference, to ensure differences at least start by decreasing
        prev_diff = datetime.max - datetime.min
        
        for row_idx, data_series in self.df.iterrows():
            new_diff = abs(datetime_obj - data_series['Weather Datetime'])
            if prev_diff < new_diff: # if local minima has just been passed
                return row_idx-1 # return index location of minima
            prev_diff = new_diff # else, continue
            
        return row_idx # if datetime_obj > all weather datetimes, return final index location
            
        
    
'''
Access csv_filepath of MasterFile written object via xxx.get_path()
'''