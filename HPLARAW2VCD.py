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
        # useful things we know about record 0
        # 0x0000 0x80 magic number inidctae HOP series 80 file
        # 0x0002 "HPSLIF" Text strin inidctaes file type
        # 0x0020 LLLLLLLL Length Big Endian format Motorola 68000
        f_magic,f_magicstr,num_records=struct.unpack(">Bx6s24xI",record[:36])
        if f_magic==0x80 and f_magicstr=="HFSLIF":
                print "Correct format file hurrah"
        #read 'directory' record
        f.seek(0x100)
        record = f.read(256)
        # useful things we know about record 1
        # 0x0100 "WS_FILE   " 10 digit filename
        # 0x0002 "HPSLIF" Text strin inidctaes file type
        # skip date as it is not used
        # 0x0020 LLLLLLLL Length Big Endian format Motorola 68000
        dirf_name,f_filetype,f_filestart,num_records,f_magic,f_implementation=struct.unpack(">10sHII6xHI",record[:32])
        if f_name[0]=="WS_FILE   ":
                print "Correct format file hurrah"
                print "dir name %s" % dirf_name
                print "f_filetype %X" % f_filetype
                print "f_filestart%X" % f_filestart
                print "numrecords %04X" % num_records
                print "f_magic %02X" % f_magic
                print "f_implementation %04X" % f_implementation
        #read first partial 'data' record
        offset=0x478
        f.seek(offset)
        pod_count=0
        print "tstamp   pod4 pod4 pod2 pod1"
        while pod_count<100:
            #bytes_read=0
            #while bytes_read<12:
                
            record = f.read(12)#timestamp plus 4 pods worth of data
            d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1=struct.unpack(">IHHHH",record[:32])
            print "%08X %04X %04X %04X %04X" % (d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1)
            pod_count+=1    
        

except ValueError:
    print "bad fing appen"
    f.close()