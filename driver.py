# -*- coding: utf-8 -*-
"""
Created on Thu Nov 26 07:24:03 2015

@author: moizr_000
"""

'''
NOTE: the range of dates supplied by this data may be slightly larger than the
range of dates specified by the user. The program reads data from the smallest
set of N complete weeks (starting on Saturdays) that encapsulate the date
range provided. This was a deliberate design decision, because subway data is 
given on a weekly basis, with the data itself only being chronological within 
each turnstile unit.
I may get around to changing the way the program reads the data files so as to
not include dates outside of the range (as opposed to deleting the 
out-of-date-range rows in the dataframe after the fact), but for the purposes 
of this project, the current code will suffice.
'''

import pandas as pd
import datetime
import turnstile_weather_dates as dates
import turnstile_weather_links as links
import file_writer
import dataframes

class Driver(object):
    def __init__(self, (start_month, start_day, start_year), (end_month, end_day, end_year), filename="turnstile_weather.csv"):
        self._make_start_end_dates((start_month, start_day, start_year), (end_month, end_day, end_year))
        MTA_dataframe = self._make_MTA_dataframe()
        WU_dataframe = self._make_WU_dataframe()
        master_dataframe = dataframes.TurnstileWeatherDataFrame(MTA_dataframe, WU_dataframe)
        self.df = master_dataframe.df
        self._write_to_csv(filename)

    def _make_start_end_dates(self, (start_month, start_day, start_year), (end_month, end_day, end_year)):
        dt_min = datetime.date(start_year, start_month, start_day)
        dt_max = datetime.date(end_year, end_month, end_day)
        self._ezdate_min = dates.EasyDate(dt_min)
        self._ezdate_max = dates.EasyDate(dt_max)
        return self
        
    def _make_MTA_dataframe(self):
        MTA_ezdates = dates.MTAEasyDateList(self._ezdate_min, self._ezdate_max)
        MTA_ezlinks = links.MTAEasyLinkList(MTA_ezdates)
        MTA_master_file = file_writer.MTAMasterFileWriter(MTA_ezlinks)
        return dataframes.MTADataFrame(MTA_master_file.get_path())
        
    def _make_WU_dataframe(self):
        WU_ezdates = dates.WUEasyDateList(self._ezdate_min, self._ezdate_max)
        WU_ezlinks = links.WUEasyLinkList(WU_ezdates)
        WU_master_file = file_writer.WUMasterFileWriter(WU_ezlinks)
        return dataframes.WUDataFrame(WU_master_file.get_path())
        
    def _write_to_csv(self, filename):
        self.df.to_csv(filename)
        return self
        
        
master_df_maker = Driver((10,1,2015), (11,1,2015))