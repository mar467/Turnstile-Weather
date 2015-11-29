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
        
    def entries_histogram(self, selection='rain'):
        if selection == 'rain':
            plt.figure()
            self.df[self.df["Events"]!='Rain']['Entries Per Hour'].hist()
            self.df[self.df["Events"]=="Rain"]['Entries Per Hour'].hist()
            return plt
        if selection == 'skies':
            plt.figure()
            self.df[self.df["Conditions"]=='Clear']['Entries Per Hour'].hist()
            self.df[self.df["Conditions"]!='Clear']['Entries Per Hour'].hist()
            return plt
        if selection == 'visibility':
            plt.figure()
            self.df[self.df["VisibilityMPH"]==10]['Entries Per Hour'].hist()
            self.df[self.df["VisibilityMPH"]!=10]['Entries Per Hour'].hist()
            return plt
        if selection == 'gusts':
            plt.figure()
            self.df[self.df["Gust SpeedMPH"]=='-']['Entries Per Hour'].hist()
            self.df[self.df["Gust SpeedMPH"]!='-']['Entries Per Hour'].hist()
            return plt
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
        
    def mann_whitney_plus_means(self, selection='rain'):
        if selection == 'rain':
            with_rain = self.df[self.df["Events"]=='Rain']['Entries Per Hour'] # series
            without_rain = self.df[self.df["Events"]!='Rain']['Entries Per Hour']
            with_rain_mean = np.mean(with_rain)
            without_rain_mean = np.mean(without_rain)
            
            print with_rain.size
            print without_rain.size
            
            U, p = scipy.stats.mannwhitneyu(with_rain, without_rain, use_continuity=True)
            return with_rain_mean, without_rain_mean, U, p
            
        if selection == 'skies':
            
            '''
            ['Clear', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy',
             'Scattered Clouds', 'Light Rain', 'Haze', 'Rain', 'Light Snow',
             'Heavy Rain', 'Snow', 'Light Freezing Rain', 'Unknown',
             'Heavy Snow', 'Mist']
             '''
       
       
            clear = self.df[self.df["Conditions"]=='Haze']['Entries Per Hour'] # series
            not_clear = self.df[self.df["Conditions"]!='Haze']['Entries Per Hour']
            clear_mean = clear.mean()
            not_clear_mean = not_clear.mean()
            
            clear.to_csv("Clear.csv")
            not_clear.to_csv("Not clear.csv")
            
            
            print clear.size
            print not_clear.size
            
            U, p = scipy.stats.mannwhitneyu(clear, not_clear, use_continuity=True)
            return clear_mean, not_clear_mean, U, p
            
        if selection == 'visibility':
            high_visibility = self.df[self.df["VisibilityMPH"]==10]['Entries Per Hour'] # series
            low_visibility = self.df[self.df["VisibilityMPH"]<2]['Entries Per Hour']
            high_visibility_mean = np.mean(high_visibility)
            low_visibility_mean = np.mean(low_visibility)
            
            print high_visibility.size
            print low_visibility.size
            
            U, p = scipy.stats.mannwhitneyu(high_visibility, low_visibility, use_continuity=True)
            return high_visibility_mean, low_visibility_mean, U, p
        
        if selection == 'gusts':
            with_gusts = self.df[self.df["Gust SpeedMPH"]=='-']['Entries Per Hour']
            without_gusts = self.df[self.df["Gust SpeedMPH"]!='-']['Entries Per Hour']
            with_gusts_mean = np.mean(with_gusts)
            without_gusts_mean = np.mean(without_gusts)
            
            print with_gusts.size
            print without_gusts.size
            
            U, p = scipy.stats.mannwhitneyu(with_gusts, without_gusts, use_continuity=True)
            return with_gusts_mean, without_gusts_mean, U, p
            
        if selection == 'wind direction':
            zero_deg = self.df[self.df["WindDirDegrees"]==0]['Entries Per Hour']
            not_zero_deg = self.df[self.df["WindDirDegrees"]!=0]['Entries Per Hour']
            zero_deg_mean = np.mean(zero_deg)
            not_zero_deg_mean = np.mean(not_zero_deg)
            
            print zero_deg.size
            print not_zero_deg.size
            
            U, p = scipy.stats.mannwhitneyu(zero_deg, not_zero_deg, use_continuity=True)
            return zero_deg_mean, not_zero_deg_mean, U, p
            
        if selection == 'precipitation':
            precip = self.df[self.df["PrecipitationIn"]>0.01]['Entries Per Hour']
            no_precip = self.df[np.isnan(self.df["PrecipitationIn"])]['Entries Per Hour']
            precip_mean = np.mean(precip)
            no_precip_mean = np.mean(no_precip)
            
            print precip.size
            print no_precip.size
            
            U, p = scipy.stats.mannwhitneyu(precip, no_precip, use_continuity=False)
            return precip_mean, no_precip_mean, U, p
            
        if selection == 'pvr':
            precip = self.df[self.df["PrecipitationIn"]>0]['Entries Per Hour']
            with_rain = self.df[self.df["Events"]=='Rain']['Entries Per Hour']
            precip_mean = np.mean(precip)
            with_rain_mean = np.mean(with_rain)
            
            print precip.size
            print with_rain.size
            
            U, p = scipy.stats.mannwhitneyu(precip, with_rain, use_continuity=True)
            return precip_mean, with_rain_mean, U, p
            
        if selection == 'temperature':
            hot = self.df[self.df["TemperatureF"]>56]['Entries Per Hour']
            cold = self.df[self.df["TemperatureF"]<56]['Entries Per Hour']
            hot_mean = np.mean(hot)
            cold_mean = np.mean(cold)
            
            print hot.size
            print cold.size
            
            U, p = scipy.stats.mannwhitneyu(hot, cold, use_continuity=True)
            return hot_mean, cold_mean, U, p