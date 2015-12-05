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
        self._make_timestamps()
        self._fill_nan_entries_exits()
        self._replace_calm_windspeeds()
        self._make_gusts_binary()
        self._fill_nan_precipitation()
        self._fill_nan_events()
        self._make_neg9999s_nans()
        self._interpolation()
        
    def _make_timestamps(self):
        self.df['Subway Datetime'] = pd.to_datetime(self.df['Subway Datetime'])
        self.df['Weather Datetime'] = pd.to_datetime(self.df['Weather Datetime'])
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        return self
        
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
        
''' Can we get rid of skies somehow? Doesn't look pretty. Also I hate the name "Analyzer"... reminds me of "Grinder" from Gears of War'''
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
        
class GradientDescent(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self.alpha = None
        self.values = None
        self.theta_gradient_descent = None
        self.cost_history = None
        self.predictions = None
        
    def _normalize_features(self, features_df):
        normalized_features_df = (features_df - features_df.mean()) / features_df.std() # normalization
        return normalized_features_df
    
    def _compute_cost(self, features, values, theta):
        predicted_values = np.dot(features, theta)
        num_values = len(values)

        cost = np.square(values - predicted_values).sum() / (2*num_values)
        return predicted_values, cost
    
    def _apply_gradient_descent(self, features, values, theta, alpha, num_iterations):
        num_values = len(values)
        cost_history = []
        predicted_values = np.dot(features, theta) # initialize
        
        for i in range(num_iterations):
            # update thetas
            theta = theta + alpha/(2*num_values)*np.dot(values - predicted_values, features)
            
            # predict new values, compute cost
            predicted_values, cost = self._compute_cost(features, values, theta)
            # append cost to history
            cost_history.append(cost)
                    
        return theta, pd.Series(cost_history)
           
    def make_predictions(self, col_name='Entries Per Hour', alpha=0.1, num_iterations=75):
        self.alpha = alpha 
        
        ''' Which column we want to predict '''
        self.values = self.df[col_name]
        
        ''' All the features that can be included in predicting the above '''
        datetime_fts = self.df[['Hour', 'Month', 'DayOfWeek', 'isWorkday', 'isHoliday']]
        dummy_subway_stations = pd.get_dummies(self.df['Station'])
        major_weather_fts = self.df[['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn']]
        minor_weather_fts = self.df[['VisibilityMPH', 'Gusts', 'PrecipitationIn', 'WindDirDegrees']]
        dummy_conditions = pd.get_dummies(self.df['Conditions']) # events naturally included in this df 
        
        ''' Which features are going to be included in predicting the above'''
        features =  datetime_fts.join([major_weather_fts, minor_weather_fts, dummy_conditions]) # change this, as fitting
        if col_name in features.columns: # do not include column itself in predicting column values
            features = features.drop([col_name], 1)
        features = self._normalize_features(features)
        features['ones'] = np.ones(len(self.values))
        
        ''' Application of Gradient Descent '''
        features_array = np.array(features)
        values_array = np.array(self.values)
        theta_gradient_descent = np.zeros(len(features.columns))
        theta_gradient_descent, cost_history = self._apply_gradient_descent(features_array, 
                                                                     values_array, 
                                                                     theta_gradient_descent, 
                                                                     alpha, 
                                                                     num_iterations) 
                                                                
        ''' Results '''
        self.theta_gradient_descent = theta_gradient_descent
        self.cost_history = cost_history
        self.predictions = np.dot(features_array, theta_gradient_descent)  
        return self
        
    def plot_cost_history(self):
        if self.alpha == None:
            print "Make predictions first."
            return
        iteration = range(len(self.cost_history))
        cost_df = pd.DataFrame({'Cost': self.cost_history, 'Iteration': iteration})
        plot = ggplot(aes(x='Iteration', y='Cost'), data=cost_df) + geom_point() + geom_line() + ggtitle('Cost History for alpha = %.3f' % self.alpha )
        return plot
        
    def plot_residuals(self):
        if self.alpha == None:
            print "Make predictions first."
            return        
        plt.figure()
        differences = self.values - self.predictions
        differences.hist(bins=range(-1000, 1500, 100))
        return plt
        
    def calculate_r_squared(self):
        if self.alpha == None:
            print "Make predictions first."
            return        
        r_squared = 1 - (np.square(self.values - self.predictions).sum())/(np.square(self.values - np.mean(self.values)).sum())
        return r_squared
        
''' Needs more cleaning. Where should group by go? Should this merge in with Analyzer? How can we clean up the plotting?
Definitely should NOT inherit from Gradient Descent, since we could use other algorithm later on.
Rather, should have function that takes in predictions from those calculations, and plot them appropriately '''
class Visualizer(GradientDescent):
    def __init__(self, turnstile_weather_df):
        GradientDescent.__init__(self, turnstile_weather_df)
        self._group_by()
        self.plot()
        # stat2.df.groupby('Month').mean()
            
    def _group_by(self, col='Date'):
        self.df = self.df.groupby(col, as_index=False).mean()
        return self

    def plot(self):
        self.df = self.df[self.df['isWorkday']==1]
        self.graph = ggplot(aes(x='Date', y='Entries Per Hour'), data=self.df) + geom_line(color='red')

    def ezplot(self):
        self.df[['Entries Per Hour', 'Predictions: Entries Per Hour']].plot()
        
        