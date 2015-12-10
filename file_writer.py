# -*- coding: utf-8 -*-
"""
Created on Sun Nov 22 10:06:49 2015

@author: moizr_000
"""

'''
The purpose of the following classes is to write master MTA and WU files given 
their respective EasyLinkList objects. The MTAMasterFileWriter class combines 
data from selected stations by reading from the multiple urls provided but 
writing in such a way to preserve the grouping of data in chronological order 
withineach turnstile unit. The WUMasterFile class, on the other hand, simply 
reads and writes all the data from the provided urls.
'''

from urllib import urlopen
import os

class MasterFileWriter(object):
    def __init__(self, filename):
        self._filename = filename
        
    def get_path(self):
        return os.path.realpath(self._filename)
    
class MTAMasterFileWriter(MasterFileWriter):
    def __init__(self, mta_ezlink_list, filename='MTA_master_file.txt', station_names=["42 ST-TIMES SQ"]):
        MasterFileWriter.__init__(self, filename)
        self._mta_ezlink_list = mta_ezlink_list
        self._station_names = station_names
        
        self._make_file()
     
    ###
            # for each station            
            # in order to put all turnstile data together
            # we need to read one single turnstile unit at a time from each data file corresponding to a week
            # then combine them together
            # and THEN move on to the next turnstile unit
    ###
    def _write_one_station(self, station_name, write_header=True):
        '''
        This specific solution avoids using x = file.tell() or file.seek(x), simply because reading a url file
        with urlopen won't allow for it. However, using these two methods would have allowed me flexibility in,
        say, obtaining data only from Times Square, or another location. An alternative could be to read each file
        entirely to a local file first, and then apply these methods, but because each file contains 190,000+
        rows of data, in the interest of time and memory, I opted against it. The present solution reads the url
        file one line at a time in order until a certain condition (max num of turnstile units) is reached.
        '''
        f_ins = [] # list of read files
        for mta_ezlink in self._mta_ezlink_list.ezlink_list:
            f_ins.append(urlopen(mta_ezlink.url))
        
        with open(self._filename, 'w') as master_file:

            last_lines = []
        
            for f_in in f_ins:
                header = f_in.readline() # skip over first line in each file
                last_lines.append(f_in.readline()) # initialize last lines list with first non-header line of each file
            
            if write_header:            
                master_file.write(header) # write the header just once

            ''' NEW ADDITION: skipping to desired station '''
            for i in range(0, len(f_ins)): # for each file...
                while last_lines[i].split(",")[3] != station_name: # while the line does not refer to the station in question
                    last_lines[i] = f_ins[i].readline() # skip the line   
        
            while(last_lines[0].split(",")[3] == station_name):
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
            
            for f_in in f_ins:
                f_in.close()
                
    def _make_file(self):
        write_header = True
        for station_name in self._station_names:
            self._write_one_station(station_name, write_header)
            write_header = False # only write the header for the first station
            
                   
class WUMasterFileWriter(MasterFileWriter):
    def __init__(self, wu_ezlink_list, filename='WU_master_file.txt'):
        MasterFileWriter.__init__(self, filename)
        self._wu_ezlink_list = wu_ezlink_list
        
        self._make_file()
    
    def _make_file(self):
        f_ins = [] # list of read files
        for wu_ezlink in self._wu_ezlink_list.ezlink_list:
            f_ins.append(urlopen(wu_ezlink.url))
            
        with open(self._filename, 'w') as master_file:

            first = True        
            for f_in in f_ins: # for each file...
                read_file = f_in.readlines()
                if first:
                    master_file.write(read_file[1]) # skip the empty line, write the header once
                    first = False
                for line in read_file[2:]:
                    master_file.write(line) # and write all the lines to the master file
                f_in.close()
