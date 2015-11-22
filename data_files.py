# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 10:06:49 2015

@author: moizr_000
"""

class MasterFileWriter(object):
    def __init__(self, filename):
        self._filename = filename
        
    def get_path(self):
        pass
    
class MTAMasterFileWriter(MasterFileWriter):
    def __init__(self, mta_ezlink_list, filename='MTA_master_file', num_scps=10):
        MasterFileWriter.__init__(self, filename)
        with open(self._filename, 'w') as master_file:
            self._first_n_scps(master_file, mta_ezlink_list, num_scps)
            
    def _first_n_scps(master_file, mta_ezlink_list, num_scps):
        pass