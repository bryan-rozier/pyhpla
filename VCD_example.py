# -*- coding: utf-8 -*-
"""
Created on Fri Aug 04 16:37:06 2017

PyVCD example

@author: bryan.rozier
"""

import sys
import os
import glob

from vcd import VCDWriter

dpath ="HP16500C_LA_FTP\slot_d\data.asc\machine1"
#these are reserved word with specific lengths as we have no way of getting this short of 
#decomposing the setting binary file (maybe one day)
addr_name = "ADDR.TXT"
addr_size = 16
data_name = "DATA.TXT"
data_size = 8

#machine_name = os.path.split(os.path.dirname(dpath))[1]
machine_name = os.path.split(dpath)[1]
machine_name="HP16555A."+machine_name

#print machine_name

with VCDWriter(sys.stdout, timescale='1 ns', date='today') as writer:
#    for filename in glob.glob(os.path.join(dpath, '*.txt')):
#        if os.path.basename(filename) == "1st_line.txt don't treat as data ":
            #print "this is the 1st line" + filename
#        else:
            #print filename
        
    counter_var = writer.register_var(machine_name, 'counter', 'integer', size=8)
    bit_var = writer.register_var(machine_name,'/M1','wire', size=1)
    addr_var = writer.register_var(machine_name,'ADDR','wire', size=16)
    for timestamp, value in enumerate(range(10, 20, 2)):
        writer.change(counter_var, timestamp, value)
        writer.change(bit_var, timestamp, value>12)
        writer.change(addr_var, timestamp, value+0xff00)
        