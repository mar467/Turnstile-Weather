# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 07:24:03 2015

@author: moizr_000
"""

'''
The purpose of the following class is to create a final .csv file of the
turnstile-weather dataframe given a desired date range, stations to be 
included, and a filename. Statistical analysis will be performed in a separate
module.
'''

import pandas as pd
import datetime
import tw_dates as dates
import tw_links as links
import file_writer
import tw_dataframes as dataframes

class Driver(object):
    def __init__(self, (start_month, start_day, start_year), (end_month, end_day, end_year), station_names=["42 ST-TIMES SQ"]):
        self.start_month = start_month
        self.start_day = start_day
        self.start_year = start_year
        self.end_month = end_month
        self.end_day = end_day
        self.end_year = end_year
        self.station_names = station_names
    
    def execute(self):
        self._make_start_end_dates()
        
        MTA_dataframe = self._make_MTA_dataframe()
        WU_dataframe = self._make_WU_dataframe()
        self.df = self._make_master_dataframe(MTA_dataframe, WU_dataframe)
        
        # self._write_to_csv()

    def _make_start_end_dates(self):
        dt_min = datetime.date(self.start_year, self.start_month, self.start_day)
        dt_max = datetime.date(self.end_year, self.end_month, self.end_day)
        self._ezdate_min = dates.EasyDate(dt_min)
        self._ezdate_max = dates.EasyDate(dt_max)
        return self
        
    def _make_MTA_dataframe(self):
        MTA_ezdates = dates.MTAEasyDateList(self._ezdate_min, self._ezdate_max)
        MTA_ezlinks = links.MTAEasyLinkList(MTA_ezdates)
        MTA_master_file = file_writer.MTAMasterFileWriter(MTA_ezlinks, station_names=self.station_names)
        return dataframes.MTADataFrame(MTA_master_file.get_path())
        
    def _make_WU_dataframe(self):
        WU_ezdates = dates.WUEasyDateList(self._ezdate_min, self._ezdate_max, start_yesterday=True)
        WU_ezlinks = links.WUEasyLinkList(WU_ezdates)
        WU_master_file = file_writer.WUMasterFileWriter(WU_ezlinks)
        return dataframes.WUDataFrame(WU_master_file.get_path())
        
    def _make_master_dataframe(self, MTA_dataframe, WU_dataframe):
        master_dataframe = dataframes.TurnstileWeatherDataFrame(MTA_dataframe, WU_dataframe)   
        cols = ['Subway Datetime', 'Weather Datetime', 'Station', 'Entries', 'Exits', 'Entries Per Hour', 'Exits Per Hour', 'Date', 'Month', 'Hour', 'DayOfWeek', 'isWorkday', 'isHoliday', 'TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'Wind SpeedMPH', 'Gust SpeedMPH', 'Wind Direction', 'WindDirDegrees', 'VisibilityMPH', 'PrecipitationIn', 'Events', 'Conditions']
        return master_dataframe.df.reindex(columns = cols)
        
    def write_to_csv(self, filename="turnstile_weather.csv"):
        self.df.to_csv(filename)
        return self
    
'''
last_two_weeks_dr = Driver((11, 27, 2015), (12, 11, 2015), station_names=["42 ST-TIMES SQ"])
last_two_weeks_dr.execute()
last_two_weeks_dr.write_to_csv(filename="last_two_weeks.csv")
'''
    
### 
        # SAMPLE CODE:
        # last_three_weeks_dr = Driver((11, 27, 2015), (12, 11, 2015), station_names=["LEXINGTON AVE", "42 ST-TIMES SQ", "42 ST-GRD CNTRL"])
        # last_three_weeks_dr.execute()
        # last_three_weeks_dr.write_to_csv(filename="last_two_weeks.csv")
###
    
# TODO: throw an error if dates provided are not chronological
'''
A few things to consider:
1. The range of dates supplied by this data may be slightly larger than the
range of dates specified by the user. The program reads data from the smallest
set of N complete weeks (starting on Saturdays) that encapsulate the date
range provided. This was a deliberate design decision, because subway data is 
given on a weekly basis, with the data itself only being chronological within 
each turnstile unit.
I may get around to changing the way the program reads the data files so as to
not include dates outside of the range (as opposed to deleting the 
out-of-date-range rows in the dataframe after the fact), but for the purposes 
of this project, the current code will suffice.
In terms of the implementation of this code, there are a few things to 
consider:
2. Since we're reading massives amount of data from the MTA website using 
urllib, the http connection may be forcibly closed before all the data can be
read. One way to get around this is to break up the date range into two or more
segments, reading those files separately, then merging them together using
pandas concatenation after.
Example:
first_half = Driver((11, 23, 2014), (5, 1, 2015), station_names=["42 ST-TIMES SQ"])
first_half.execute()
second_half = Driver((5, 4, 2014), (11, 28, 2015), station_names=["42 ST-TIMES SQ"])
second_half.execute()
master_df = pd.concat([first_half.df, second_half.df], ignore_index=True)
master_df.to_csv('times_square_turnstile_weather.csv')
3. Less recent MTA data may be unformatted, which won't allow my code to work
as desired for dates before 2013 or so. In a future modification of this 
project, I may figure out a way to download all the MTA data as text files
first, and then read from them without using urllib. This will drastically
speed up runtime, and allow me much more flexibility in wrangling the raw data.
But for now, I think it is cooler that my code is able to extract data directly 
off the MTA website as opposed to local text files.
'''
 

'''
NOTE TO SELF: Time Square Station Turnstile Unit 01-00-07 loses all its data on 11/21/2014 @ 15:00:00
http://web.mta.info/developers/data/nyct/turnstile/turnstile_141122.txt
So to get the full year of data, go from 11/23-28/2014 to 11/23-28/2015
'''
# TODO: allow ability to change holiday daterange in tw_dataframes module
# to match range of dates provided