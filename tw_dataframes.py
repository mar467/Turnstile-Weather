# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:11:28 2015

@author: moizr_000
"""

'''
The purpose of the following classes is to merge an MTA and WU dataframe into
a master turnstile-weather dataframe with all the major structural features
necessary for analysis. The MTADataFrame class does the brunt of this work,
by summing all turnstile entries and exits in a given station for every audit 
event, then calculating entries and exits per hour using the cumulative data.
The TurnstileWeatherDataFrame class is responsible for merging this dataframe
and the weather underground dataframe together by pairing each entries or exits
per hour entry with the weather event that occured at the audit event just 
prior to it.
'''

# a note on terminology:
# 'df' is used to refer to a pandas.DataFrame object
# 'dataframe' is used to refer to the object created by these classes

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar

class DataFrame(object):
    def __init__(self):
        self.df = pd.DataFrame()


class MTADataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self)
        self.df = pd.read_csv(csv_filepath)
        self._clean_up()
        
        self._make_datetime_col()
        self._combine_scps_all_stations()
        self._make_hourly_entries_col()
        self._make_hourly_exits_col()
        
    def _clean_up(self):
        new_columns = []
        for i in range(len(self.df.columns)):
            new_columns.append(self.df.columns[i].strip().title())
        self.df.columns = new_columns
        return self

    def _make_datetime_col(self, add_more_cols=True):
        datetimes = pd.to_datetime(self.df['Date']+' '+self.df['Time'], format='%m/%d/%Y %H:%M:%S')       
        self.df['Subway Datetime'] = datetimes

        if add_more_cols:
            self.df['Date'] = datetimes.apply(lambda dt: dt.date())
            self.df['Month'] = datetimes.apply(lambda dt: dt.month)
            self.df['Hour'] = datetimes.apply(lambda dt: dt.hour)
            self.df['DayOfWeek'] = datetimes.apply(lambda dt: dt.dayofweek)
            self.df['isWorkday'] = self.df['DayOfWeek'].apply(lambda weekday: 1 if weekday<5 else 0)
            
            calendar = USFederalHolidayCalendar()
            holidays = calendar.holidays(start='2014-11-19', end='2015-12-31')
            self.df['isHoliday'] = self.df['Date'].apply(lambda date: 1 if date in holidays else 0)
        
        return self
        
    ###
        # The following method combines data from ALL the turnstile units within a single subway station
        # This makes subsequent statistical analysis easier
        # scp = sub channel position (turnstile unit identifier)
    ###
    def _combine_scps(self, station_df):
        # TODO: This code might be able to be written more cleanly
        # using Pandas split-apply-combine methods
        # group by scp... where count < 8, extrapolate
        
        def end_index_first_scp(df, zeroeth_index):
            first_scp = df.loc[zeroeth_index, 'Scp']
            for row_idx, data_series in df.iterrows():
                if data_series['Scp'] != first_scp:
                    return row_idx - 1
        
        old_df = station_df
        
        scp_arr = old_df['Scp'].unique().tolist()
        
        zeroeth_index = old_df.index[0]
        end_first_scp = end_index_first_scp(old_df, zeroeth_index)
        new_df = old_df.loc[zeroeth_index:end_first_scp] # make a new df, consisting of only first scp in old_df

        for row_idx, data_series in new_df.iterrows():
            # dataframe consisting of the data for all scps for a given date
            all_scps_for_date_df = old_df[old_df['Subway Datetime']==data_series['Subway Datetime']]
            
            additional_entries = 0
            additional_exits = 0 
            ###
            # the following code is in case there is a missing value in one the turnstiles for a specific datetime                   
            # if there is, the code will add the missing entries/exits to addtional_entries/exits respectively
            # it does this by predicting what the missing entries/exits would be by taking the average of the
            # entries/exits of the datetime before it with the same for the datetime after it
            if all_scps_for_date_df['Scp'].size != len(scp_arr):
                all_scps = all_scps_for_date_df['Scp'].tolist()
                missed_scps = list(set(scp_arr) - set(all_scps))
                
                for scp in missed_scps:
                    # NOTE: in some cases, there may be an instance where the new_df read
                    # will contain an odd time (say, 7:51 pm)
                    # and no other scp will match that time
                    # this will manifest itself as this code trying to predict the other 7 turnstiles
                    # not desirable, of course, but is not currently a problem
                    # maybe fix later?
                
                    this_scp_df = old_df[old_df['Scp'] == scp]
                    
                    before_dt = this_scp_df[this_scp_df['Subway Datetime'] < data_series['Subway Datetime']]             
                    last_before_dt = before_dt.iloc[-1]                  
                    
                    after_dt = this_scp_df[this_scp_df['Subway Datetime'] > data_series['Subway Datetime']]                   
                    first_after_dt = after_dt.iloc[0]
                    
                    additional_entries += (last_before_dt['Entries'] + first_after_dt['Entries'])/2.0
                    additional_exits += (last_before_dt['Exits'] + first_after_dt['Exits'])/2.0
            ###
            new_df.loc[row_idx, 'Entries'] = np.sum(all_scps_for_date_df['Entries']) + additional_entries
            new_df.loc[row_idx, 'Exits'] = np.sum(all_scps_for_date_df['Exits']) + additional_exits

        return new_df 
        
    def _combine_scps_all_stations(self):
        stations = self.df['Station'].unique().tolist()
        new_df_list = []
        for station in stations:
            station_df = self.df[self.df['Station']==station]
            new_df = self._combine_scps(station_df)
            new_df_list.append(new_df)

        self.df = pd.concat(new_df_list, ignore_index=True)
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

    
class WUDataFrame(DataFrame):
    def __init__(self, csv_filepath):
        DataFrame.__init__(self)
        self.df = pd.read_csv(csv_filepath)
        self._clean_up()
        
        self._make_datetime_col()
        
    def _clean_up(self):
        pass
    
    def _make_datetime_col(self):
        self.df['Weather Datetime'] = pd.to_datetime(self.df['DateUTC<br />'], format="%Y-%m-%d %H:%M:%S<br />") - timedelta(hours = 4) # needed to convert supplied datetimes to EDT
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
            
class TurnstileWeatherDataFrame(DataFrame): # TAKES IN PANDAS DATAFRAMES!
    def __init__(self, MTA_dataframe, WU_dataframe):
        DataFrame.__init__(self)
        self._merge_dataframes(MTA_dataframe, WU_dataframe)
        
    # the first helper method in executing merge of MTA_ and WU_dataframes
    # returns index location of closest weather datetime given a datetime object
    # efficient because avoids searching through all weather datetimes
    def _closest_wu_datetime(self, WU_df, datetime_obj):
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
        
        for row_idx, data_series in WU_df.iterrows():
            new_diff = abs(datetime_obj - data_series['Weather Datetime'])
            if prev_diff < new_diff: # if local minima has just been passed
                return row_idx-1 # return index location of minima
            prev_diff = new_diff # else, continue
            
        return row_idx # if datetime_obj > all weather datetimes, return final index location
        
    # second helper method in executing merge of MTA_ and WU_dataframes, using above method within it  
    # returns closest weather datetime INDEXES corresponding to entire subway datetime series
    # efficient because avoids restarting at start of WU_dataframe datetimes for each MTA datetime comparison search
    def _closest_wu_datetimes(self, WU_df, MTA_df):
        '''
        The strategy here is to again use the chronology of datetimes in both dataframes advantageously. Basically,
        as we iterate through each datetime in the MTA_dataframe, we record what the WU_dataframe index location of
        the previous closest match was. This way, we can start there next time, rather than at the beginning of the
        WU_dataframe for every iteration. This speeds up the process drastically.
        '''
        
        # defines a Series with an index identical to the MTA_dataframe...
        # but to be filled with the index locations of the closest WU_dataframe datetimes!
        # this is designed in such a way to make merging the WU_dataframe into the MTA_dataframe as simple as possible
        closest_indexes = pd.Series(0, index=MTA_df.index)
        
        start_of_wu_df = WU_df.index[0]
        
        prev_wu_idx = start_of_wu_df # initialize 'where we last left off' index to start of WU_dataframe
        
        # prev_mta_dt necessary to know for when mta datetimes reach end of turnstile unit, and cycle over from first date     
        ''' CHANGE: initialize prev_mta_dt to first mta_dt - 4 hours instead of below: '''        
        # prev_mta_dt = datetime.min # initialize to datetime smallest value to start
        prev_mta_dt = MTA_df.iloc[0]['Subway Datetime'] - timedelta(hours=4)
        
        for mta_idx, data_series in MTA_df.iterrows():
            curr_mta_dt = data_series["Subway Datetime"]
            
            # if subway datetimes cycle to end of loop (i.e.: reached end of turnstile unit, going to next)
            if(prev_mta_dt > curr_mta_dt):
                # start over at beginning of WU_dataframe again
                prev_wu_idx = start_of_wu_df
                ''' NEW ADDITION: reset prev_mta_dt here '''
                prev_mta_dt = curr_mta_dt - timedelta(hours=4)
            
            # note the .loc[prev_wu_idx:]
            # this has the effect of starting at where last left off in the WU_dataframe, to save time
            ''' CHANGE: use prev_mta_dt instead of curr_mta_dt '''            
            closest_wu_idx = self._closest_wu_datetime(WU_df.loc[prev_wu_idx:], prev_mta_dt)
            
            closest_indexes[mta_idx] = closest_wu_idx
            
            prev_wu_idx = closest_wu_idx # enable continuation of where last left off
            prev_mta_dt = curr_mta_dt # again, to check if reached end of turnstile unit (when prev_mta_dt becomes greater than curr_mta_dt)
            
        return closest_indexes
        
    # third helper method, that simply returns an updated weather df to be concatenated to existing MTA_dataframe
    def _updated_weather_df(self, WU_df, MTA_df):
        corresponding_wu_idxs = self._closest_wu_datetimes(WU_df, MTA_df)
        
        updated_weather_df = pd.DataFrame(index=corresponding_wu_idxs.index, columns=WU_df.columns)
        
        for new_idx, wu_idx in corresponding_wu_idxs.iteritems():
            updated_weather_df.iloc[new_idx] = WU_df.iloc[wu_idx]
            
        return updated_weather_df
        
    # finally, use all these helper methods to create a final merged dataframe  
    def _merge_dataframes(self, MTA_dataframe, WU_dataframe):
        MTA_df = MTA_dataframe.df
        WU_df = WU_dataframe.df
        upd_wu_df = self._updated_weather_df(WU_df, MTA_df)
        self.df = pd.concat([MTA_dataframe.df, upd_wu_df], axis=1)
        return self
