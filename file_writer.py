# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 10:06:49 2015

@author: moizr_000
"""

from urllib import urlopen
import os

class MasterFileWriter(object):
    def __init__(self, filename):
        self._filename = filename
        
    def get_path(self):
        return os.path.realpath(self._filename)
    
class MTAMasterFileWriter(MasterFileWriter):
    def __init__(self, mta_ezlink_list, filename='MTA_master_file.txt', num_scps=4):
        MasterFileWriter.__init__(self, filename)
        
        self._f_ins = [] # list of read files
        for mta_ezlink in mta_ezlink_list.ezlink_list:
            self._f_ins.append(urlopen(mta_ezlink.url))
        
        with open(self._filename, 'w') as master_file:
            self._first_n_scps(master_file, self._f_ins, num_scps)
            
     
    ###
            # in order to put all turnstile data together
            # we need to read one single turnstile unit at a time from each data file corresponding to a week
            # then combine them together
            # and THEN move on to the next turnstile unit
    ###
     
    def _first_n_scps(self, master_file, f_ins, num_scps=8): # scp = sub channel position (turnstile unit identifier)
        '''
        This specific solution avoids using x = file.tell() or file.seek(x), simply because reading a url file
        with urlopen won't allow for it. However, using these two methods would have allowed me flexibility in,
        say, obtaining data only from Times Square, or another location. An alternative could be to read each file
        entirely to a local file first, and then apply these methods, but because each file contains 190,000+
        rows of data, in the interest of time and memory, I opted against it. The present solution reads the url
        file one line at a time in order until a certain condition (max num of turnstile units) is reached.
        '''

        last_lines = []
        
        for f_in in f_ins:
            header = f_in.readline() # skip over first line in each file
            last_lines.append(f_in.readline()) # initialize last lines list with first non-header line of each file
            
        master_file.write(header) # write the header just once

        ''' NEW ADDITION: skipping to Times Square '''
        for i in range(0, len(f_ins)): # for each file...
            while last_lines[i].split(",")[3] != "42 ST-TIMES SQ": # while the line does not refer to Times Square
                last_lines[i] = f_ins[i].readline() # skip the line        
        
        scp_num = 0
        
        while(scp_num < num_scps):     
            for i in range(0, len(f_ins)): # for each file...
                master_file.write(last_lines[i]) # write the line last left off at
                prev_line = last_lines[i]
                curr_line = f_ins[i].readline()
                
                # finds index location of third coma
                segs = prev_line.split(",")
                idx = len(segs[0]+segs[1]+segs[2]) + 3
                
                while prev_line[0:idx] == curr_line[0:idx]: # and while still on the same turnstile unit...
                    master_file.write(curr_line) # keep writing lines for this file
                    prev_line = curr_line
                    curr_line = f_ins[i].readline()
                    
                last_lines[i] = curr_line # record the line of the first new turnstile unit
                # repeat the process for next file
            scp_num += 1
            
        for f_in in f_ins:
            f_in.close()
            
            
class WUMasterFileWriter(MasterFileWriter):
    def __init__(self, wu_ezlink_list, filename='WU_master_file.txt'):
        MasterFileWriter.__init__(self, filename)
        
        self._f_ins = [] # list of read files
        for wu_ezlink in wu_ezlink_list.ezlink_list:
            self._f_ins.append(urlopen(wu_ezlink.url))
            
        with open(self._filename, 'w') as master_file:
            self._make_file(master_file, self._f_ins)

    ###
        # much simpler
        # can just be writen in entirely (excepting header) one at a time to master file
    ###    
    
    def _make_file(self, master_file, f_ins):
        first = True        
        for f_in in f_ins: # for each file...
            read_file = f_in.readlines()
            if first:
                master_file.write(read_file[1]) # skip the empty line, write the header once
                first = False
            for line in read_file[2:]:
                master_file.write(line) # and write all the lines to the master file
            f_in.close()
