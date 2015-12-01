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
from ggplot import ggplot, aes, geom_point, ggtitle
from datetime import datetime

class WrangledDataFrame(object):
    def __init__(self, turnstile_weather_df):
        self.df = turnstile_weather_df
        self._replace_calm_windspeeds()
        self._replace_dashes_gusts()
        self._make_neg9999s_nans()
        self.interpolation()
        self._fillna()
        self._make_hour_col() # move to tw_dataframes
        
    '''
    def only_include_busy_turnstiles(self):
        self.df = self.df[self.df['Entries'] > 10000]
        self.df['Entries Per Hour'] = self.df['Entries Per Hour'].fillna(0)
    '''
    
    def _replace_calm_windspeeds(self, val=0):
        self.df['Wind SpeedMPH'].replace('Calm', val, inplace=True)
        return self
        
    def _replace_dashes_gusts(self):
        self.df['Gust SpeedMPH'].replace('-', np.nan, inplace=True)
        return self
        
    def _make_neg9999s_nans(self):
        cols = ['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'VisibilityMPH', 'Wind SpeedMPH']
        for col in cols:        
            self.df.loc[:,col].replace(-9999, np.nan, inplace=True)
        return self
        
    def interpolation(self):
        # NOTE: wind speed not included because only category that can vary drastically between 4 hour periods
        cols = ['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'VisibilityMPH']
        for col in cols:        
            self.df.loc[:,col].interpolate(inplace=True)
        self.df.loc[:,"Wind SpeedMPH"].interpolate(inplace=True)
        return self
        
    def _fillna(self):
        cols = ['Entries Per Hour', 'Exits Per Hour']
        for col in cols:
            self.df.loc[:,col].fillna(0, inplace=True)
        return self
        
    def _make_hour_col(self): # move to tw_dataframes
        self.df['Hour'] = pd.Series('', index=self.df.index)
        self.df['Day'] = pd.Series('', index=self.df.index)
        self.df['Month'] = pd.Series('', index=self.df.index)
        self.df['Weekday'] = pd.Series('', index=self.df.index)
        self.df['isWeekend'] = pd.Series(0, index=self.df.index)
        for row_idx, data_series in self.df.iterrows():
            datetime_str = data_series["Subway Datetime"]
            datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
            self.df.loc[row_idx, 'Hour'] = datetime_obj.hour
            self.df.loc[row_idx, 'Day'] = datetime_obj.day
            self.df.loc[row_idx, 'Month'] = datetime_obj.month
            self.df.loc[row_idx, 'Weekday'] = datetime_obj.weekday()
            if datetime_obj.weekday() > 4:
                self.df.loc[row_idx, 'isWeekend'] = 1
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
        
        
class GradientDescent(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self.df = turnstile_weather_df
        predictions, plot = self._make_predictions()
        self.predictions = predictions
        
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
        
    def _make_predictions(self):
        '''
        CLEAN THIS UP!!!
        Fix features
        Move R^2 prediction to separate method
        '''        
        
        
        features = self.df[['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn']]
        # 'Hour', 'Day', 'Month', 'Weekday'
        dummy_conditions = pd.get_dummies(self.df['Conditions'], prefix='unit')
        
        features = features.join(dummy_conditions)
        features = self._normalize_features(features)
        
        values = self.df['Entries Per Hour']
        
        features['ones'] = np.ones(len(values))

        
        features_array = np.array(features)
        values_array = np.array(values)
        
        alpha = .1
        num_iterations = 150
        
        theta_gradient_descent = np.zeros(len(features.columns))
        theta_gradient_descent, cost_history = self._apply_gradient_descent(features_array, 
                                                                     values_array, 
                                                                     theta_gradient_descent, 
                                                                     alpha, 
                                                                     num_iterations)
        plot = None                                                          
        #plot = self._plot_cost_history(alpha, cost_history)
        
        data = self.df['Entries Per Hour']
        predictions = np.dot(features_array, theta_gradient_descent)
        r_squared = 1 - (np.square(data - predictions).sum())/(np.square(data - np.mean(data)).sum())
        print r_squared
        
        return predictions, plot
        
    def _plot_cost_history(self, alpha, cost_history):
        
        cost_df = pd.DataFrame({ 'Cost_History': cost_history, 'Iteration': range(len(cost_history))})
        
        return ggplot(cost_df, aes('Iteration', 'Cost History')) + geom_point() + ggtitle('Cost History for alpha = %.3f' % alpha )
        
        
        