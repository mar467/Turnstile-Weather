# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 11:11:28 2015

@author: moizr_000
"""

import pandas

class DataFrame(object):
    def __init__(self, csv_filepath):
        self.df = pandas.read_csv(csv_filepath)
        
