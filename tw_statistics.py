# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 07:14:08 2015

@author: moizr_000
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import scipy.stats

class WrangledDataFrame(object):
    def __init__(self, turnstile_weather_df):
        self.df = turnstile_weather_df
        
    '''
    def only_include_busy_turnstiles(self):
        self.df = self.df[self.df['Entries'] > 10000]
        self.df['Entries Per Hour'] = self.df['Entries Per Hour'].fillna(0)
    '''
        
class Analyzer(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        
    def _condition(self, selection, skies):
        ''' 
        skies:
            ['Clear', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy',
             'Scattered Clouds', 'Light Rain', 'Haze', 'Rain', 'Light Snow',
             'Heavy Rain', 'Snow', 'Light Freezing Rain', 'Unknown',
             'Heavy Snow', 'Mist']
        '''
             
        if selection == 'rain':
            with_cond = self.df["Events"]=='Rain'
            without_cond = self.df["Events"]!='Rain'
            
        elif selection == 'skies': # needs to catch potential errors with skies
            with_cond = self.df["Conditions"]==skies
            without_cond = self.df["Conditions"]!=skies
            
        elif selection == 'visibility':
            with_cond = self.df["VisibilityMPH"]==10
            without_cond = self.df["VisibilityMPH"]<10

        elif selection == 'gusts':
            with_cond = self.df["Gust SpeedMPH"]=='-' # FIX AFTER WRANGLED
            without_cond = self.df["Gust SpeedMPH"]!='-' # FIX AFTER WRANGLED
            
        elif selection == 'wind direction':
            with_cond = self.df["WindDirDegrees"]==0
            without_cond = self.df["WindDirDegrees"]!=0
      
        elif selection == 'precipitation':
            with_cond = self.df["PrecipitationIn"]>0.01
            without_cond = self.df[np.isnan(self.df["PrecipitationIn"])] # FIX AFTER WRANGLED
            
        elif selection == 'temperature':
            with_cond = self.df["TemperatureF"]>50
            without_cond = self.df["TemperatureF"]<50
            
        elif selection == 'humidity':
            with_cond = self.df["Humidity"]>56
            without_cond = self.df["Humidity"]<56
  
        elif selection == 'pressure':
            with_cond = self.df["Sea Level PressureIn"]>33
            without_cond = self.df["Sea Level PressureIn"]<33
            
        else:
            print 'Not a valid selection.'
            with_cond = self.df["Events"]=='Rain'
            without_cond = self.df["Events"]!='Rain'
            
        return with_cond, without_cond
            
        
    def entries_histogram(self, selection='rain', skies='Clear', opposite=False):
        if opposite:
            without_cond, with_cond = self._condition(selection, skies)
        else:
            with_cond, without_cond = self._condition(selection, skies)
        
        plt.figure()
        self.df[with_cond]['Entries Per Hour'].hist()
        self.df[without_cond]['Entries Per Hour'].hist()
        return plt
        
    def mann_whitney_plus_means(self, selection='rain', skies='Clear'):
        with_cond, without_cond = self._condition(selection, skies)
        
        cond = self.df[with_cond]['Entries Per Hour']
        no_cond = self.df[without_cond]['Entries Per Hour']
        cond_mean = np.mean(cond)
        no_cond_mean = np.mean(no_cond)
        
        U, p = scipy.stats.mannwhitneyu(cond, no_cond, use_continuity=True)
        return (cond.size, cond_mean), (cond.size, no_cond_mean), U, p
        