# -*- coding: utf-8 -*-
"""
Created on Fri Aug 04 16:37:06 2017

Read ascii files from HP16555A logic analyzer card and create a a
Verilog VCD format file
This can be viewed in GTKWave
It is a nice example of using the PyVCD module

@author: bryan.rozier
"""

import sys
import os
import glob

from vcd import VCDWriter
# fixed data path for now eventually move to command line arguments
dpath ="HP16500C_LA_FTP\slot_d\data.asc\machine1"
#these are reserved word with specific lengths as we have no way of getting this short of 
#decomposing the setting binary file (maybe one day)
addr_name = "addr"
addr_size = 16
data_name = "data"
data_size = 8

#machine_name = os.path.split(os.path.dirname(dpath))[1]
machine_name = os.path.split(dpath)[1]

# this card supports upto two 'machines' pods can be assigned between them
machine_name="HP16555A."+machine_name

#print machine_name
file_list = []# full relative path of ascii files
var_list = []
signal_list = []
file_handle_list=[]
prev_line = []

try:
    with VCDWriter(sys.stdout, timescale='1 ns', date='today',init_timestamp=0) as writer:
        # figure out what signals ther are
        # each signal has its own file
        for filename in glob.glob(os.path.join(dpath, '*.txt')):
            if os.path.basename(filename) != "1st_line.txt":
                file_list.append(os.path.basename(filename))
        # re-order list so line number and absolute time at start
        #find line number
        old_index = file_list.index("line_num.txt")
        #then move it:
        file_list.insert(0, file_list.pop(old_index))   
        #find time
        old_index = file_list.index("time_abs.txt")
        #then move it:
        file_list.insert(1, file_list.pop(old_index))   
        
        # create list of signals using the filename list
        # strictly this is wrong e should use the first line in each file as the 
        # data name
        for filename in file_list:
            if filename != "1st_line.txt":
                signal_list.append(os.path.splitext(filename)[0])
        # create list of vcd variables using the filename as the variable name
        # not strictly correct as the first line in each data file is its
        # true label as displayed by the LA
        for signal in signal_list:
            if signal == addr_name:
                size=addr_size
            elif signal == data_name:
                size=data_size
            else:
                size=1
            if signal!='line_num' and signal!='time_abs':
                # create a vcd variable for each signal
                var_list.append(writer.register_var(machine_name, signal, 'wire', size))   
            else:
                #create a dummy entry in the variable list as we don't want to display these two
                var_list.append(0)
        #open all the filez
        for filename in file_list:
            file_handle_list.append(open(dpath+"\\"+filename)) #defaults to read only
            
        #scan through each file until emppty
        ftimestamp = 0.0
        timestamp=0
        init_timestamp=0
        line_count =0
        #while line_count <10:
        #use above line for tetsing
        while True:
            file_count=0
    #        for file_handle,signal,var in file_handle_list,signal_list,var_list:
            for file_handle in file_handle_list:
                line=file_handle.readline()
                #first line in file is a label we'll ignore that at the moment
                if line_count !=0:
                    if signal_list[file_count]!='line_num' and signal_list[file_count]!='time_abs':
                        #print signal_list[file_count]
                        if prev_line[file_count]!=line:
                            # assume all lines are hex this works okay for binary too
                            writer.change(var_list[file_count], timestamp, int(line.rstrip(),16))
                            prev_line[file_count]=line
                    elif signal_list[file_count]=='time_abs':
                        if line_count==1:
                            #store initial timestamp
                            ftimestamp=float(line.rstrip())
                            init_timestamp=int(ftimestamp*1e9) # convert to whole number
                            timestamp=0
                        else:
                            ftimestamp=float(line.rstrip())
                            timestamp=int(ftimestamp*1e9)-init_timestamp # convert to whole number
                        
                else:
                    #store variable name as previous value bound nt to repeat! bit of a hack
                    prev_line.insert(file_count,line)
                
                file_count+=1
            
            line_count+=1
            
except ValueError:
    for file_handle in file_handle_list:
        file_handle.close()
