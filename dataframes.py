# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:11:28 2015

@author: moizr_000
"""

import pandas as pd
from datetime import datetime, timedelta

class DataFrame(object):
    def __init__(self):
        self.df = pd.DataFrame()
        
class MTADataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self)
        self.df = pd.read_csv(csv_filepath)
        
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
        DataFrame.__init__(self)
        self.df = pd.read_csv(csv_filepath)
        
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
            
            
### TurnstileWeatherDataFrame class:
    # purpose is to combine MTA dataframe and WU dataframe into one master dataframe
    # because the MTA datetimes and WU datetimes don't match exactly,
    # the purpose of this class is to find the CLOSEST matches between the two
    # and write them together into a master dataframe
    # because the difference between closest matches is on the order of 9 minutes
    # this won't sacrifice much accuracy (weather does not change much in that time)
    # also note: since the weather data is taken far more frequently than subway data
    # some weather data might not find its way to the final dataframe
###
            
class TurnstileWeatherDataFrame(DataFrame):
    def __init__(self, MTA_dataframe, WU_dataframe):
        DataFrame.__init__(self)
        self._merge_dataframes(MTA_dataframe, WU_dataframe)
        
    # the first helper method in executing merge of MTA_ and WU_dataframes
    # returns index location of closest weather datetime given a datetime object
    # efficient because avoids searching through all weather datetimes
    def _closest_wu_datetime(WU_dataframe, datetime_obj):
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
        
        for row_idx, data_series in WU_dataframe.df.iterrows():
            new_diff = abs(datetime_obj - data_series['Weather Datetime'])
            if prev_diff < new_diff: # if local minima has just been passed
                return row_idx-1 # return index location of minima
            prev_diff = new_diff # else, continue
            
        return row_idx # if datetime_obj > all weather datetimes, return final index location
        
    # second helper method in executing merge of MTA_ and WU_dataframes, using above method within it  
    # returns closest weather datetime INDEXES corresponding to entire subway datetime series
    # efficient because avoids restarting at start of WU_dataframe datetimes for each MTA datetime comparison search
    def _closest_wu_datetimes(self, WU_dataframe, MTA_dataframe):
        '''
        The strategy here is to again use the chronology of datetimes in both dataframes advantageously. Basically,
        as we iterate through each datetime in the MTA_dataframe, we record what the WU_dataframe index location of
        the previous closest match was. This way, we can start there next time, rather than at the beginning of the
        WU_dataframe for every iteration. This speeds up the process drastically.
        '''
        
        # defines a Series with an index identical to the MTA_dataframe...
        # but to be filled with the index locations of the closest WU_dataframe datetimes!
        # this is designed in such a way to make merging the WU_dataframe into the MTA_dataframe as simple as possible
        closest_indexes = pd.Series(0, index=MTA_dataframe.df.index)
        
        start_of_wu_df = WU_dataframe.df.index[0]
        
        prev_wu_idx = start_of_wu_df # initialize 'where we last left off' index to start of WU_dataframe
        # prev_mta_dt necessary to know for when mta datetimes reach end of turnstile unit, and cycle over from first date     
        prev_mta_dt = datetime.min # initialize to datetime smallest value to start
        
        for mta_idx, data_series in MTA_dataframe.df.iterrows():
            curr_mta_dt = data_series["Subway Datetime"]
            
            # if subway datetimes cycle to end of loop (i.e.: reached end of turnstile unit, going to next)
            if(prev_mta_dt > curr_mta_dt):
                # start over at beginning of WU_dataframe again
                prev_wu_idx = start_of_wu_df
            
            # note the .loc[prev_wu_idx:]
            # this has the effect of starting at where last left off in the WU_dataframe, to save time
            closest_wu_idx = self._closest_wu_datetime(WU_dataframe, MTA_dataframe.df.loc[prev_wu_idx:])
            
            closest_indexes[mta_idx] = closest_wu_idx
            
            prev_wu_idx = closest_wu_idx # enable continuation of where last left off
            prev_mta_dt = curr_mta_dt # again, to check if reached end of turnstile unit (when prev_mta_dt becomes greater than curr_mta_dt)
            
        return closest_indexes
        
    # third helper method, that simply returns an updated weather df to be concatenated to existing MTA_dataframe
    def _updated_weather_df(self, WU_dataframe, MTA_dataframe):
        corresponding_wu_idxs = self._closest_wu_datetimes(WU_dataframe, MTA_dataframe)
        
        updated_weather_df = pd.DataFrame(index=corresponding_wu_idxs.index, columns=WU_dataframe.df.columns)
        
        for new_idx, wu_idx in corresponding_wu_idxs.iteritems():
            updated_weather_df.iloc[new_idx] = WU_dataframe.df.iloc[wu_idx]
            
        return updated_weather_df
        
    # finally, use all these helper methods to create a final merged dataframe  
    def _merge_dataframes(self, MTA_dataframe, WU_dataframe):
        upd_wu_df = self._updated_weather_df(WU_dataframe, MTA_dataframe)
        self.df = pd.concat([MTA_dataframe.df, upd_wu_df], axis=1)
        return self