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
        
    def entries_histogram(self, selection='rain', skies='Clear'):
        ''' 
        skies:
            ['Clear', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy',
             'Scattered Clouds', 'Light Rain', 'Haze', 'Rain', 'Light Snow',
             'Heavy Rain', 'Snow', 'Light Freezing Rain', 'Unknown',
             'Heavy Snow', 'Mist']
        '''
        
        if selection == 'rain':
            plt.figure()
            self.df[self.df["Events"]!='Rain']['Entries Per Hour'].hist()
            self.df[self.df["Events"]=="Rain"]['Entries Per Hour'].hist()
            return plt
        if selection == 'skies':
            plt.figure()
            self.df[self.df["Conditions"]==skies]['Entries Per Hour'].hist()
            self.df[self.df["Conditions"]!=skies]['Entries Per Hour'].hist()
            return plt
        if selection == 'visibility':
            plt.figure()
            self.df[self.df["VisibilityMPH"]==10]['Entries Per Hour'].hist()
            self.df[self.df["VisibilityMPH"]!=10]['Entries Per Hour'].hist()
            return plt
        '''
        if selection == 'gusts':
            plt.figure()
            self.df[self.df["Gust SpeedMPH"]=='-']['Entries Per Hour'].hist() # FIX AFTER WRANGLED
            self.df[self.df["Gust SpeedMPH"]!='-']['Entries Per Hour'].hist() # FIX AFTER WRANGLED
            return plt
        '''
        if selection == 'wind direction':
            plt.figure()
            self.df[self.df["WindDirDegrees"]==0]['Entries Per Hour'].hist()
            self.df[self.df["WindDirDegrees"]!=0]['Entries Per Hour'].hist()
            return plt
        if selection == 'humidity':
            plt.figure()
            self.df[self.df["Humidity"]>56]['Entries Per Hour'].hist()
            self.df[self.df["Humidity"]<56]['Entries Per Hour'].hist()
            return plt
        if selection == 'temperature':
            plt.figure()
            self.df[self.df["TemperatureF"]>50]['Entries Per Hour'].hist()
            self.df[self.df["TemperatureF"]<50]['Entries Per Hour'].hist()
            return plt
        print "Not a valid selection."
        
    def mann_whitney_plus_means(self, selection='rain', skies='Clear'):
        ''' 
        skies:
            ['Clear', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy',
             'Scattered Clouds', 'Light Rain', 'Haze', 'Rain', 'Light Snow',
             'Heavy Rain', 'Snow', 'Light Freezing Rain', 'Unknown',
             'Heavy Snow', 'Mist']
        '''
             
        if selection == 'rain':
            with_rain = self.df[self.df["Events"]=='Rain']['Entries Per Hour'] # series
            without_rain = self.df[self.df["Events"]!='Rain']['Entries Per Hour']
            with_rain_mean = np.mean(with_rain)
            without_rain_mean = np.mean(without_rain)
            
            with_rain_size = with_rain.size
            without_rain_size = without_rain.size
            
            U, p = scipy.stats.mannwhitneyu(with_rain, without_rain, use_continuity=True)
            return (with_rain_size, with_rain_mean), (without_rain_size, without_rain_mean), U, p
            
        if selection == 'skies':
            cond = self.df[self.df["Conditions"]==skies]['Entries Per Hour'] # series
            not_cond = self.df[self.df["Conditions"]!=skies]['Entries Per Hour']
            cond_mean = cond.mean()
            not_cond_mean = not_cond.mean()
            
            cond_size = cond.size
            not_cond_size = not_cond.size
            
            U, p = scipy.stats.mannwhitneyu(cond, not_cond, use_continuity=True)
            return (cond_size, cond_mean), (not_cond_size, not_cond_mean), U, p
            
        if selection == 'visibility':
            high_visibility = self.df[self.df["VisibilityMPH"]==10]['Entries Per Hour'] # series
            low_visibility = self.df[self.df["VisibilityMPH"]<2]['Entries Per Hour']
            high_visibility_mean = np.mean(high_visibility)
            low_visibility_mean = np.mean(low_visibility)
            
            high_visibility_size = high_visibility.size
            low_visibility_size = low_visibility.size
            
            U, p = scipy.stats.mannwhitneyu(high_visibility, low_visibility, use_continuity=True)
            return (high_visibility_size, high_visibility_mean), (low_visibility_size, low_visibility_mean), U, p
        
        '''
        if selection == 'gusts':
            with_gusts = self.df[self.df["Gust SpeedMPH"]=='-']['Entries Per Hour'] # FIX AFTER WRANGLED
            without_gusts = self.df[self.df["Gust SpeedMPH"]!='-']['Entries Per Hour'] # FIX AFTER WRANGLED
            with_gusts_mean = np.mean(with_gusts)
            without_gusts_mean = np.mean(without_gusts)
            
            with_gusts_size = with_gusts.size
            without_gusts_size = without_gusts.size
            
            U, p = scipy.stats.mannwhitneyu(with_gusts, without_gusts, use_continuity=True)
            return (with_gusts_size, with_gusts_mean), (without_gusts_size, without_gusts_mean), U, p
        '''
            
        if selection == 'wind direction':
            zero_deg = self.df[self.df["WindDirDegrees"]==0]['Entries Per Hour']
            not_zero_deg = self.df[self.df["WindDirDegrees"]!=0]['Entries Per Hour']
            zero_deg_mean = np.mean(zero_deg)
            not_zero_deg_mean = np.mean(not_zero_deg)
            
            zero_deg_size = zero_deg.size
            not_zero_deg_size = not_zero_deg.size
            
            U, p = scipy.stats.mannwhitneyu(zero_deg, not_zero_deg, use_continuity=True)
            return (zero_deg_size, zero_deg_mean), (not_zero_deg_size, not_zero_deg_mean), U, p
            
        if selection == 'precipitation':
            precip = self.df[self.df["PrecipitationIn"]>0.01]['Entries Per Hour']
            no_precip = self.df[np.isnan(self.df["PrecipitationIn"])]['Entries Per Hour']
            precip_mean = np.mean(precip)
            no_precip_mean = np.mean(no_precip)
            
            precip_size = precip.size
            no_precip_size = no_precip.size
            
            U, p = scipy.stats.mannwhitneyu(precip, no_precip, use_continuity=True)
            return (precip_size, precip_mean), (no_precip_size, no_precip_mean), U, p
            
            
        if selection == 'temperature':
            hot = self.df[self.df["TemperatureF"]>56]['Entries Per Hour']
            cold = self.df[self.df["TemperatureF"]<56]['Entries Per Hour']
            hot_mean = np.mean(hot)
            cold_mean = np.mean(cold)
            
            hot_size = hot.size
            cold_size = cold.size
            
            U, p = scipy.stats.mannwhitneyu(hot, cold, use_continuity=True)
            return (hot_size, hot_mean), (cold_size, cold_mean), U, p