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
from datetime import datetime, timedelta

'''
The purpose of the following classes are to wrangle, analyze, visualize, and
model the csv dataset created from previous modules. The sample code below
demonstrates their implementation.

################################ SAMPLE CODE: ################################

df = pd.read_csv('turnstile_weather.csv')

visualizer = Visualizer(df)
print visualizer.plot('Date', 'Entries Per Hour')
print visualizer.weekdays_only().plot('Date', 'Entries Per Hour')
print visualizer.workdays_only().plot('Date', 'Entries Per Hour')
print visualizer.weekends_only().plot('Date', 'Entries Per Hour')

explorer = Explorer(df)
explorer.plot_entries_histogram('cloudy vs clear skies', opposite=True)
print explorer.mann_whitney_plus_means('cloudy vs clear skies')
explorer.workdays_only().plot_entries_histogram('cloudy vs clear skies')
print explorer.workdays_only().mann_whitney_plus_means('cloudy vs clear skies')
explorer.non_workdays_only().plot_entries_histogram('cloudy vs clear skies')
print explorer.non_workdays_only().mann_whitney_plus_means('cloudy vs clear skies')

predictor = GradientDescentPredictor(df)
predictor.make_predictions('Entries Per Hour')
#print predictor.plot_cost_history()
#predictor.plot_residuals()
print predictor.calculate_r_squared()

visualizer.include_predictions(predictor.predictions)
visualizer.comparison_plot(grouping='Date')
visualizer.weekdays_only().comparison_plot(grouping='Date')
visualizer.workdays_only().comparison_plot(grouping='Date')
visualizer.weekends_only().comparison_plot(grouping='Date')

last_two_weeks_df = pd.read_csv('last_two_weeks.csv')

last_two_weeks_predictor = GradientDescentPredictor(last_two_weeks_df)
last_two_weeks_predictor.make_predictions_with_thetas(predictor)
predictions = last_two_weeks_predictor.predictions

last_two_weeks_visualizer = Visualizer(last_two_weeks_df)
last_two_weeks_visualizer.include_predictions(predictions)
last_two_weeks_visualizer.comparison_plot()
print last_two_weeks_predictor.calculate_r_squared()

##############################################################################
'''

class WrangledDataFrame(object):
    def __init__(self, turnstile_weather_df):
        self.df = turnstile_weather_df
        self._wrangle()
        
    def _wrangle(self):
        self._make_timestamps()
        self._fill_nan_entries_exits()
        self._replace_calm_windspeeds()
        self._make_gusts_binary()
        self._fill_nan_precipitation()
        self._fill_nan_events()
        self._make_neg9999s_nans()
        self._interpolation()
        self._near_holidays()
        # self._make_temperature_var_col()
        
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
        cols = ['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn', 'VisibilityMPH'] #, 'Wind SpeedMPH']
        for col in cols:        
            self.df.loc[:,col].interpolate(inplace=True)
        self.df.loc[:,"Wind SpeedMPH"].interpolate(inplace=True)
        return self
        
    def _near_holidays(self, val_to_assign=1):
        # assigns holiday value to black friday, christmas eve,
        # day after christmas, new year's eve, and day after new year's        
        
        black_fri_date = None
        for row_idx, data_series in self.df.iterrows():
            date = data_series['Date']
            dayofyear = date.dayofyear
            if dayofyear > 326:
                if date.month == 11:
                    if data_series['isHoliday']==1: # is thanksgiving
                        black_fri_date = date + timedelta(days=1)
                    elif date == black_fri_date:
                        self.df.loc[row_idx, 'isHoliday'] = val_to_assign
                else: # date.month == 12
                    day = date.day
                    if day == 24 or day == 26 or day == 31:
                        self.df.loc[row_idx, 'isHoliday'] = val_to_assign
            elif dayofyear == 2:
                self.df.loc[row_idx, 'isHoliday'] = val_to_assign
        
        return self
        
    '''
    def _make_temperature_var_col(self, pct_diff = 10):
        self.df["Temperature Var"] = pd.Series(0, index=self.df.index)
        
        temp_df = self.df.groupby("Date", as_index=False).mean()
        prev_temp = temp_df.loc[0, "TemperatureF"]
        
        for row_idx, data_series in temp_df.iterrows():
            diff = (data_series["TemperatureF"] - prev_temp)/(prev_temp)*100.0
            
            if diff > pct_diff:
                self.df[self.df["Date"]==data_series["Date"]].loc[:, "Temperature Var"] = 1
            if diff > -pct_diff:
                self.df[self.df["Date"]==data_series["Date"]].loc[:, "Temperature Var"] = -1        
                
            prev_temp = data_series["TemperatureF"]
            
        return self
    '''


class TailoredDataFrame(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self._original = self.df
        self._grouped = False
        self._tailored = False
        
    def include_predictions(self, predictions):
        if self._grouped or self._tailored:
            self.return_to_original()
        predictions = np.asarray(predictions, np.float64)
        self.df['Predictions'] = pd.Series(predictions, index=self.df.index)             
        return self
        
    def group_by(self, category='Date'):
        self.df = self.df.groupby(category, as_index=False).mean()
        self._grouped = True
        return self
        
    def weekdays_only(self, make_original=True):
        if make_original or self._tailored:
            self.return_to_original()
        self.df = self.df[self.df['isWorkday']==1]
        self._tailored = True
        return self
        
    def weekends_only(self, make_original=True):
        if make_original or self._tailored:
            self.return_to_original()
        self.df = self.df[self.df['isWorkday']==0]
        self._tailored = True
        return self
        
    def workdays_only(self, make_original=True):
        if make_original or self._tailored:
            self.return_to_original()
        self.df = self.df[(self.df['isWorkday']==1) & (self.df['isHoliday']==0)]
        self._tailored = True
        return self
        
    def non_workdays_only(self, make_original=True):
        if make_original or self._tailored:
            self.return_to_original()
        self.df = self.df[(self.df['isWorkday']==0) | (self.df['isHoliday']==1)]
        self._tailored = True
        return self
    
    def return_to_original(self):
        self.df = self._original
        self._grouped = False
        self._tailored = False
        return self


class Explorer(TailoredDataFrame):
    def __init__(self, turnstile_weather_df):
        TailoredDataFrame.__init__(self, turnstile_weather_df)
        
    def _condition(self, selection):
        ''' 
        conditions:
            ['Clear', 'Mostly Cloudy', 'Overcast', 'Partly Cloudy',
             'Scattered Clouds', 'Light Rain', 'Haze', 'Rain', 'Light Snow',
             'Heavy Rain', 'Snow', 'Light Freezing Rain', 'Unknown',
             'Heavy Snow', 'Mist']
        '''
        
        if selection == 'rain':
            with_cond = self.df["Events"]=='Rain'
            without_cond = self.df["Events"]!='Rain'
            
        elif selection == 'snow':
            with_cond = self.df["Events"]=='Snow'
            without_cond = self.df["Events"]!='Snow'
            
        elif selection == 'cloudy vs clear skies': 
            with_cond = self.df["Conditions"].isin(['Mostly Cloudy', 'Overcast', 'Partly Cloudy', 'Scattered Clouds'])
            without_cond = self.df["Conditions"]=='Clear'
            
        elif selection == 'haze and mist':
            with_cond = self.df["Conditions"].isin(['Haze', 'Mist'])
            without_cond = with_cond==False
            
        elif selection == 'visibility':
            with_cond = self.df["VisibilityMPH"]==10
            without_cond = self.df["VisibilityMPH"]<10
            
        elif selection == 'wind speed':
            mean = np.mean(self.df["Wind SpeedMPH"])
            with_cond = self.df["Wind SpeedMPH"]>mean
            without_cond = self.df["Wind SpeedMPH"]<mean

        elif selection == 'gusts':
            with_cond = self.df["Gusts"]==1
            without_cond = self.df["Gusts"]==0
      
        elif selection == 'precipitation':
            with_cond = self.df["PrecipitationIn"]>0
            without_cond = self.df["PrecipitationIn"]==0
            
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
        
    def plot_entries_histogram(self, selection='rain', opposite=False):
        if opposite:
            without_cond, with_cond = self._condition(selection)
        else:
            with_cond, without_cond = self._condition(selection)
        
        plt.figure()
        self.df[with_cond]['Entries Per Hour'].hist()
        self.df[without_cond]['Entries Per Hour'].hist()
        plt.xlabel('Entries Per Hour')
        plt.ylabel('Frequency')
        plt.title('Entries/Hr Distributions for Two Different Conditions')
        return plt
        
    def mann_whitney_plus_means(self, selection='rain'):
        with_cond, without_cond = self._condition(selection)
        
        cond = self.df[with_cond]['Entries Per Hour']
        no_cond = self.df[without_cond]['Entries Per Hour']
        cond_mean = np.mean(cond)
        no_cond_mean = np.mean(no_cond)    
        
        U, p = scipy.stats.mannwhitneyu(cond, no_cond, use_continuity=True)
        return (cond.size, cond_mean), (no_cond.size, no_cond_mean), U, p
    
    
class Visualizer(TailoredDataFrame):
    def __init__(self, turnstile_weather_df):
        TailoredDataFrame.__init__(self, turnstile_weather_df)

    def plot(self, x_col_name='Date', y_col_name='Entries Per Hour'):
        self.group_by(x_col_name)
        plot = ggplot(aes(x=x_col_name, y=y_col_name), data=self.df) + geom_line(color='red') + ggtitle('Average '+y_col_name+' vs. '+x_col_name)
        return plot
        
    def hourly_bar_plot(self):
        regular_hours = (self.df.groupby('Hour').count()['Entries Per Hour']>2)
        plot = self.df.groupby('Hour').mean()[regular_hours][['Entries Per Hour']].plot(kind='bar')
        plot.set_ylabel('Average Entries Per Hour')
        plot.set_title('Average Entries Per Hour by Hour')
        return plot
        
    '''
    def multiple(self):
        regular_hours = (self.df.groupby('Hour').count()['Exits Per Hour']>2)
        df1=self.workdays_only().df.groupby('Hour').mean()[regular_hours][['Exits Per Hour']]
        df1.rename(columns={'Exits Per Hour':'Workday Exits Per Hour'}, inplace=True)
        df2=self.non_workdays_only().df.groupby('Hour').mean()[regular_hours][['Exits Per Hour']]
        df2.rename(columns={'Exits Per Hour':'Non-Workday Exits Per Hour'}, inplace=True)
        plot=df1.join(df2).plot(kind='bar')
        plot.set_ylabel('Average Exits Per Hour')
        plot.set_title('Average Exits Per Hour by Hour')
        return plot
    '''
        
    def daily_bar_plot(self):
        plot = self.df.groupby('DayOfWeek').mean()[['Entries Per Hour']].plot(kind='bar')
        plot.set_xlabel('Day of Week (0 = Monday)')
        plot.set_ylabel('Average Entries Per Hour')
        plot.set_title('Average Entries Per Hour by Day of Week')
        return plot

    def comparison_plot(self, first_col_name='Entries Per Hour', second_col_name='Predictions', grouping=None):

        if grouping is None:
            grouping_name='Audit event'
            average = ''
        else:
            self.group_by(grouping)
            grouping_name=grouping
            average = 'Average '
            
        plot = self.df[[first_col_name, second_col_name]].plot()
        plot.set_xlabel(grouping_name)
        plot.set_ylabel(average+first_col_name)
        plot.set_title('Predicted vs. Expected '+first_col_name+' by '+grouping_name)
        return plot
   
     
class GradientDescentPredictor(WrangledDataFrame):
    def __init__(self, turnstile_weather_df):
        WrangledDataFrame.__init__(self, turnstile_weather_df)
        self.col_name = None
        self.alpha = None
        self.values = None
        self.thetas = None
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
        
    def create_features_df(self):
        ''' All the features that can be included in predicting '''
        fts = self.df[[]]
        
        # self.df["Hour"] = self.df["Hour"].apply(lambda x: 0 if x==23 else x + x%2)
        
        dummy_hours_by_day = self.df[[]]
        linearized_hours = self.df[[]]
        
        days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i in range(len(days_of_week)):
            curr_weekday_df = self.df[self.df['DayOfWeek']==i]
            
            dummies = pd.get_dummies(curr_weekday_df['Hour'], prefix=days_of_week[i]+' hour: ')
            dummy_hours_by_day = dummy_hours_by_day.join([dummies])
            
            avg_hrly_entries = curr_weekday_df.groupby('Hour').mean()['Entries Per Hour']
            hr_max = avg_hrly_entries.idxmax() # hour of max number of average entries/hr
            hr_min = avg_hrly_entries.idxmin() # hour of min number of average entries/hr
            linearized_hours[days_of_week[i]+' lin hour'] = curr_weekday_df['Hour'].apply(lambda hr: (hr-hr_max)**3.3 if (hr>hr_max) else abs(hr-hr_min)**3.3) # treating it as ~cube-root helps slightly
            
        dummy_hours_by_day = dummy_hours_by_day.fillna(0)
        linearized_hours = linearized_hours.fillna(0)
        
        dummy_months = pd.get_dummies(self.df['Month'], prefix='month: ') 
        
        # self.df['isWorkday'] = abs(self.df['isHoliday']-1)*self.df['isWorkday'] # changing isWorkday (which is actually isWeekday) to actually isWorkday
        datetime_fts = self.df[['isHoliday']].join([dummy_hours_by_day, dummy_months, linearized_hours])

        dummy_subway_stations = pd.get_dummies(self.df['Station'])
        major_weather_fts = self.df[['TemperatureF', 'Dew PointF', 'Humidity', 'Sea Level PressureIn']]
        minor_weather_fts = self.df[['VisibilityMPH', 'Gusts', 'PrecipitationIn', 'WindDirDegrees']]
        dummy_conditions = pd.get_dummies(self.df['Conditions'], prefix='condition: ') # events naturally included in this df 
        dummy_events = pd.get_dummies(self.df['Events'], prefix='event: ')        
        
        ''' Which features are going to be included in predicting '''             
        features =  fts.join([datetime_fts, major_weather_fts, minor_weather_fts, dummy_conditions, dummy_events]) # change this, as fitting
        features = self._normalize_features(features)
        features['ones'] = np.ones(len(dummy_months)) # y-intercept
        
        return features
           
    def make_predictions(self, col_name='Entries Per Hour', alpha=0.1, num_iterations=75):
        self.col_name = col_name
        self.alpha = alpha 
        
        ''' Which column we want to predict '''
        self.values = self.df[col_name]
        values_array = np.array(self.values)

        ''' Features to include '''
        self.features = self.create_features_df()
        if col_name in self.features.columns: # do not include column itself in predicting column values
            self.features = features.drop([col_name], 1)
        features_array = np.array(self.features)
        
        ''' Application of Gradient Descent '''
        theta_gradient_descent = np.zeros(len(self.features.columns))
        theta_gradient_descent, cost_history = self._apply_gradient_descent(features_array, 
                                                                     values_array, 
                                                                     theta_gradient_descent, 
                                                                     alpha, 
                                                                     num_iterations) 
                                                                
        ''' Results '''
        self.thetas = theta_gradient_descent
        self.cost_history = cost_history
        self.predictions = np.dot(features_array, theta_gradient_descent)
        self.predictions[self.predictions<0]=0 # making it so there are no negative values
        return self
        
    def make_predictions_with_thetas(self, PredictorObject):  
        # for the purposes of later plotting
        col_name = PredictorObject.col_name        
        self.values = self.df[col_name]
        
        # making features
        self.features = self.create_features_df()
        
        # reindexing features to match thetas obtained from other gradient descent object
        other_columns = PredictorObject.features.columns 
        self.features = self.features.reindex(columns=other_columns)
        self.features = self.features.fillna(0)
        
        features_array = np.array(self.features)
        self.predictions = np.dot(features_array, PredictorObject.thetas)
        return self
            
    def plot_cost_history(self):
        if self.cost_history is None:
            print "Run make_predictions() first."
            return
        iteration = range(len(self.cost_history))
        cost_df = pd.DataFrame({'Cost': self.cost_history, 'Iteration': iteration})
        plot = ggplot(aes(x='Iteration', y='Cost'), data=cost_df) + geom_point() + geom_line() + ggtitle('Cost History for alpha = %.3f' % self.alpha )
        return plot
        
    def plot_residuals(self):
        if self.predictions is None:
            print "Make predictions first."
            return        
        plt.figure()
        differences = self.values - self.predictions
        differences.hist(bins=range(-500, 500, 25))
        plt.title('Residual Plot for alpha = %.3f' % self.alpha )
        plt.xlabel('Residuals')
        plt.ylabel('Frequency')
        return plt
        
    def calculate_r_squared(self):
        if self.predictions is None:
            print "Make predictions first."
            return        
        r_squared = 1 - (np.square(self.values - self.predictions).sum())/(np.square(self.values - np.mean(self.values)).sum())
        return r_squared