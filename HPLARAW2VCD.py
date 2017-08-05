# -*- coding: utf-8 -*-
"""
Created on Sat Aug 05 18:11:56 2017

Try to extract LA data from HP1655A card binary form.

Need to reverse engineer the file format.
@author: bryan.rozier
"""
import struct 
# fixed data path for now eventually move to command line arguments
dname ="HP16500C_LA_FTP\slot_d\data.raw"
sname ="HP16500C_LA_FTP\slot_d\setup.raw"

try:
    with open(dname, "rb") as f:
        f.seek(0) # not needed here 
        record_count=0
        byte=0
        #while byte != "" and record_count <256:
        while byte != "" and record_count <25:
            # Do stuff with byte.
            byte = f.read(1)
            i = ord(byte)   # Get the integer value of the byte
            hex = "{0:x}".format(i) # hexadecimal: ff
            #print "%04X %s %02X %c" % (record_count, hex, i, i)
            print "%04X %02X %c" % (record_count, i, i)
            record_count+=1
        #read first record
        f.seek(0)
        record = f.read(256)
        f_magic,f_magicstr=struct.unpack("cx6s",record[:8])

except ValueError:
    for file_handle in file_handle_list:
        file_handle.close()
