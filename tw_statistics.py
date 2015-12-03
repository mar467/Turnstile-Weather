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
from ggplot import *
from datetime import datetime

class WrangledDataFrame(object):
    def __init__(self, turnstile_weather_df):
        self.df = turnstile_weather_df
        self._fill_nan_entries_exits()
        self._replace_calm_windspeeds()
        self._make_gusts_binary()
        self._fill_nan_precipitation()
        self._fill_nan_events()
        self._make_neg9999s_nans()
        self._interpolation()
        
                
    def _fill_nan_entries_exits(self):
        cols = ['Entries Per Hour', 'Exits Per Hour']
        for col in cols:
            self.df.loc[:,col].fillna(0, inplace=True)
        return self        
    
    def _replace_calm_windspeeds(self, val=0):
        self.df['Wind SpeedMPH'].replace('Calm', val, inplace=True)
        self.df['Wind SpeedMPH'] = self.df['Wind SpeedMPH'].astype(float)
        return self
        
    def _make_gusts_binary(self):
        self.df.rename(columns={'Gust SpeedMPH': 'Gusts'}, inplace=True)
        self.df['Gusts'].replace('-', 0, inplace=True)
        for row_idx, gust_speed in self.df['Gusts'].iteritems():
            if gust_speed > 0:
                self.df.loc[row_idx, 'Gusts'] = 1
        return self
        
    def _fill_nan_precipitation(self):
        self.df['PrecipitationIn'].fillna(0, inplace=True)
        return self
        
    def _fill_nan_events(self):
        self.df['Events'].fillna('None', inplace=True)
        return self
        
    def _make_neg9999s_nans(self):
        cols = ['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'VisibilityMPH', 'Wind SpeedMPH']
        for col in cols:        
            self.df.loc[:,col].replace(-9999, np.nan, inplace=True)
        return self
        
    def _interpolation(self):
        # NOTE: wind speed interpolated, despite fact that it can vary drastically between 4 hour periods
        cols = ['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'VisibilityMPH', 'Wind SpeedMPH']
        for col in cols:        
            self.df.loc[:,col].interpolate(inplace=True)
        self.df.loc[:,"Wind SpeedMPH"].interpolate(inplace=True)
        return self
        
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
            mean = np.mean(self.df["TemperatureF"])
            with_cond = self.df["TemperatureF"]>mean
            without_cond = self.df["TemperatureF"]<mean
            
        elif selection == 'humidity':
            mean = np.mean(self.df["Humidity"])
            with_cond = self.df["Humidity"]>mean
            without_cond = self.df["Humidity"]<mean
  
        elif selection == 'pressure':
            mean = np.mean(self.df["Sea Level PressureIn"])
            with_cond = self.df["Sea Level PressureIn"]>mean
            without_cond = self.df["Sea Level PressureIn"]<mean
            
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
        
class Visualizer(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self._make_timestamps()
        self.plot()
        
    def _make_timestamps(self):
        self.df['Timestamp'] = pd.Series(0, index=self.df.index)
        for row_idx, data_series in self.df.iterrows():
            self.df.loc[row_idx, 'Timestamp'] = pd.to_datetime(data_series['Subway Datetime'])

    def plot(self):
        self.graph = ggplot(aes(x='Timestamp', y='Entries Per Hour'), data=self.df) + geom_line(color='red')

        
class GradientDescent(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self.df = turnstile_weather_df
        self._make_predictions()

        
    def _normalize_features(self, features_df):
        normalized_features_df = (features_df - features_df.mean()) / features_df.std() # normalization
        return normalized_features_df
    
    def _compute_cost(self, features, values, theta):
        actual_values = values
        predicted_values = np.dot(features, theta)
        num_values = len(values)

        cost = np.square(actual_values - predicted_values).sum() / (2*num_values)
        
        return cost
    
    def _apply_gradient_descent(self, features, values, theta, alpha, num_iterations):
        actual_values = values
        num_values = len(values)
        cost_history = []
        
        for i in range(num_iterations):
            predicted_values = np.dot(features, theta)
            
            # update thetas
            theta = theta + alpha/(2*num_values)*np.dot(actual_values - predicted_values, features)
            
            cost_history.append(self._compute_cost(features, values, theta))
                    
        return theta, pd.Series(cost_history)
        
    def _plot_cost_history(self, alpha, cost_history):
        # Stupidly enough, the name of the X or Y cannot exceed 4 characters...
        iteration = range(len(cost_history))
        cost_df = pd.DataFrame({'Cost': cost_history, 'Iter': iteration})
        plot = ggplot(aes(x='Iter', y='Cost'), data=cost_df) + geom_point() + geom_line() + ggtitle('Cost History for alpha = %.3f' % alpha )
        self.cost_history_plot = plot
        return self
        
    def _plot_residuals(self, data, predictions):
        plt.figure()
        differences = data - predictions
        differences.hist(bins=range(-1000, 1500, 100))
        self.residual_plot = plt
        return self
        
    def _calculate_r_squared(self, data, predictions):
        r_squared = 1 - (np.square(data - predictions).sum())/(np.square(data - np.mean(data)).sum())
        self.r_squared = r_squared
        return self
    
        
    def _make_predictions(self):
        ###
        datetime_fts = self.df[['Hour', 'Day', 'Month', 'DayOfWeek', 'isWorkday', 'isHoliday']]
        dummy_subway_stations = pd.get_dummies(self.df['Station'])
        major_weather_fts = self.df[['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn']]
        minor_weather_fts = self.df[['VisibilityMPH', 'Gusts', 'PrecipitationIn', 'WindDirDegrees']]
        dummy_conditions = pd.get_dummies(self.df['Conditions']) # events naturally included in this df 
        ###
        
        # which of the above features to include in predictive analysis
        features =  datetime_fts.join([major_weather_fts, minor_weather_fts, dummy_conditions])
        features = self._normalize_features(features)
        
        # what we are attempting to predict
        values = self.df['Entries Per Hour']
        
        # necessary column of 1s (y-intercept)
        features['ones'] = np.ones(len(values))

        features_array = np.array(features)
        values_array = np.array(values)
        
        ''' Application of Gradient Descent '''
        alpha = .1
        num_iterations = 75
        theta_gradient_descent = np.zeros(len(features.columns))
        theta_gradient_descent, cost_history = self._apply_gradient_descent(features_array, 
                                                                     values_array, 
                                                                     theta_gradient_descent, 
                                                                     alpha, 
                                                                     num_iterations) 
                                                                
        ''' Predictions '''   
        self.predictions = np.dot(features_array, theta_gradient_descent)
        
        ''' Cost History Plot '''
        self._plot_cost_history(alpha, cost_history)
        
        ''' Residual Plot '''
        self._plot_residuals(values, self.predictions)
        
        ''' R-Squared Value '''
        self._calculate_r_squared(values, self.predictions)
        
        return self
        

        
        
        