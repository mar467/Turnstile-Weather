# -*- coding: utf-8 -*-
"""
Created on Fri Nov 20 09:31:18 2015

@author: moizr_000
"""

import dates

class Link(object):
    def __init__(self):
        self.url = ""
        
    def get_url(self):
        return self.url
        
class MTALink(Link):
    def __init__(self, subway_date):
        Link.__init__(self)
        self.date = subway_date
        self.make_url()
        
    def make_url():
        pass # will need to use subway_date.get_[day, month, year]()
    
        