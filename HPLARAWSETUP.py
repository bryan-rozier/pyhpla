# -*- coding: utf-8 -*-
"""
Created on Sun Aug 06 16:35:40 2017

@author: bryan.rozier
"""

import struct 
# fixed data path for now eventually move to command line arguments
dname ="HP16500C_LA_FTP\slot_d\data.raw"
sname ="HP16500C_LA_FTP\slot_d\setup.raw"

try:
    with open(sname, "rb") as f:
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
            #print "%04X %02X %c" % (record_count, i, i)
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
        f_name,f_filetype,f_filestart,num_records,f_magic,f_implementation=struct.unpack(">10sHII6xHI",record[:32])
        if f_name[0]=="WS_FILE   ":
                print "Correct format file hurrah"
                print "dir name %s" % dirf_name
                print "f_filetype %X" % f_filetype
                print "f_filestart%X" % f_filestart
                print "numrecords %04X" % num_records
                print "f_magic %02X" % f_magic
                print "f_implementation %04X" % f_implementation
        #read first partial 'data' record
        offset=0x4B4
        f.seek(offset)
        num_records-=2# data starts in 3rd record I think
        pod_count=0
        print "label,unknown1,lformat,polarity,weird_offset,unknown_offset,width,enable,sequence,b4"
        while pod_count<20:
        #while num_records>1:#last one seems to be corrupt
            bytes_read=0
            string=""
            while bytes_read<22:
                if offset % 0x100==0:# on a record boundary
                    offset+=2# skip over two record header bytes 00FE except on last one
                    f.seek(offset)
                    num_records-=1
                    #print "%08X" % offset
                string+=f.read(1)
                bytes_read+=1
                offset+=1
                
            record=string
            #print "%08X" % offset
            #print record,len(record)
            #record = f.read(12)#timestamp plus 4 pods worth of data
            #d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1=struct.unpack(">IHHHH",record[:32])
            label,unknown1,lformat,polarity,weird_offset,unknown_offset,width,enable,sequence,b4=struct.unpack(">6sHBBLLBBBB",record[:22])
            print "%s %04X %02X %02X %08X %08X %02d %02X %02X %02X" % (label,unknown1,lformat,polarity,weird_offset,unknown_offset,width,enable,sequence,b4)
            pod_count+=1
            if width==0:
                break
        #print "%08X %04X %04X %04X %04X" % (d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1)

except ValueError:
    print "bad fing appen"
    f.close()
