# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 07:14:08 2015

@author: moizr_000
"""

import numpy as np
import pandas
import matplotlib.pyplot as plt

class TurnstileWeatherStatistics(object):
    def __init__(self, turnstile_weather_df):
        self.df = turnstile_weather_df
        
class ExploratoryAnalysis(TurnstileWeatherStatistics):
    def __init__(self, turnstile_weather_df):
        TurnstileWeatherStatistics.__init__(self, turnstile_weather_df)
        
    def entries_histogram(self):
        plt.figure()
        # self.df[self.df["Events"]!='Rain']['Entries Per Hour'].hist()
        self.df[self.df["Events"]=="Rain"]['Entries Per Hour'].hist()
        return plt