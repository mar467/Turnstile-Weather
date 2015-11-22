# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 10:06:49 2015

@author: moizr_000
"""

from urllib import urlopen

class MasterFileWriter(object):
    def __init__(self, filename):
        self._filename = filename
        
    def get_path(self):
        pass
    
class MTAMasterFileWriter(MasterFileWriter):
    def __init__(self, mta_ezlink_list, filename='MTA_master_file', num_scps=10):
        MasterFileWriter.__init__(self, filename)
        
        self._f_ins = [] # list of read files
        for ezlink in mta_ezlink_list.ezlink_list:
            self._f_ins.append(urlopen(ezlink.url))
        
        with open(self._filename, 'w') as master_file:
            self._first_n_scps(master_file, self._f_ins, num_scps)
            
     
    ###
            # in order to put all turnstile data together
            # we need to read one single turnstile unit at a time from each data file corresponding to a week
            # then combine them together
            # and THEN move on to the next turnstile unit
    ###
     
    def _first_n_scps(master_file, f_ins, num_scps): # scp = sub channel position (turnstile unit identifier)

        last_lines = []
        
        for f_in in f_ins:
            header = f_in.readline() # skip over first line in each files
            last_lines.append(f_in.readline()) # initialize last lines list with first non-header line of each file
            
        master_file.write(header) # write the header just once
        
        scp_num = 0
        
        while(scp_num < num_scps):     
            for i in range(0, len(f_ins)): # for each file...
                master_file.write(last_lines[i]) # write the line last left off at
                prev_line = last_lines[i]
                curr_line = f_ins[i].readline()
                
                while prev_line[0:19] == curr_line[0:19]: # and while still on the same turnstile unit...
                    master_file.write(curr_line) # keep writing lines for this file
                    prev_line = curr_line
                    curr_line = f_ins[i].readline()
                    
                last_lines[i] = curr_line # record the line of the first new turnstile unit
                # repeat the process for next file
            scp_num += 1