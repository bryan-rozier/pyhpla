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
        if dirf_name=="WS_FILE   ":
                print "Correct format file hurrah"
                print "dir name %s" % dirf_name
                print "f_filetype %X" % f_filetype
                print "f_filestart%X" % f_filestart
                print "numrecords %04X" % num_records
                print "f_magic %02X" % f_magic
                print "f_implementation %04X" % f_implementation
        #read 'DATA' record
        f.seek(0x200)
        record = f.read(256)
        r_marker,r_len,r_description=struct.unpack(">HI32s",record[:38])
        if r_marker==0x00FE:
                print "Found: Start of record 0x00FE"
                print "r_len %08X (%d Bytes)" % (r_len,r_len)
                print "r_string %s" % r_description
        # useful things we know about record 1
        #The 16 bytes of the section header are as follows:
        #Byte Position
        #1 10 bytes - Section name ("DATA space space space space space
        #             space" in ASCII for the DATA instruction).
        #11 1 byte - Reserved
        #12 1 byte - Module ID (34 decimal for the HP 16554A and HP 16555A/D master
        #            boards, and 35 for expander boards)
        #13 4 bytes - Length of block in bytes that when converted to decimal, specifies
        #             the number of bytes contained in the data block.
        # 0x0226 "DATA      " 10 digit filename
        # 0x0002 "HPSLIF" Text string inidctaes file type
        # skip date as it is not used
        # 0x0020 LLLLLLLL Length Big Endian format Motorola 68000
        dictionary = {34:"HP 16554/5A Master",35:"Expander Board"}
        d_name,d_reserved,d_ModuleID,block_len=struct.unpack(">10sBBI",record[0x26:0x26+16])
        if d_name=="DATA      ":
                print "Found:" + d_name
                print "d_ModuleID %s" % dictionary[d_ModuleID]
                print "block_len %08X (%d Bytes)" % (block_len,block_len)
        # Data Preamble
        dict_AnalyzerID = {0:"HP16554A Master",1:"HP16555A"}
        dict_MachineDataMode = {-1:"off",
                                 0:"70 MHz (HP 16554A) or 100 MHz (HP 16555A/D) State data, no tags",
                                 1:"70 MHz (HP 16554A) or 100 MHz (HP 16555A/D) State data with tags",
                                 2:"70 MHz (HP 16554A) or 100 MHz (HP 16555A/D) State data with tags",
                                 3:"Fast State data, no tags (HP 16555A/D)",
                                 4:"Fast State data with tags (HP 16555A/D)",
                                 5:"Fast State data with tags (HP 16555A/D)",
                                10:"conventional timing data on all channels",
                                13:"conventional timing data on half channels"}#
        dict_TagType = {0:"off",1:"time tags",2:"state tags"}
        p_InstrumentID,p_RevisionCode,p_NumAcqChips,p_AnalyzerID,p_MachineDataMode,p_PodList,p_MasterChip,p_MemDepth,p_unused1,p_SamplePeriod_ps,p_TagType,p_TriggerOffset,p_unused2=struct.unpack(">IIIIIIIIIQIQ30s",record[0x36:0x36+86])
        if p_InstrumentID==16500:#as its on a HP16500C
                print "Found p_InstrumentID:%d" % p_InstrumentID
                print "p_RevisionCode  %08X" % p_RevisionCode
                print "p_NumAcqChips  %08X"% p_NumAcqChips
                print "p_AnalyzerID  %s"% dict_AnalyzerID[p_AnalyzerID]
                print "p_MachineDataMode  %s"% dict_MachineDataMode[p_MachineDataMode]
                print "p_PodList  %08X"% p_PodList
                print "p_MasterChip  %08X"% p_MasterChip
                print "p_MemDepth  %08X"% p_MemDepth
                print "p_SamplePeriod_ps  %016X (%d)"% (p_SamplePeriod_ps,p_SamplePeriod_ps)
                print "p_TagType  %s"% dict_TagType[p_TagType]
                print "p_TriggerOffset  %016X" % p_TriggerOffset
        
        #read first partial 'data' record
        offset=0x478
        f.seek(offset)
        num_records-=2# data starts in 3rd record I think
        pod_count=0
        print "tstamp   pod4 pod4 pod2 pod1"
        while pod_count<100:
        #while num_records>1:#last one seems to be corrupt
            bytes_read=0
            string=""
            while bytes_read<12:
                if offset % 0x100==0:# on a record boundary
                    offset+=2# skip over two record header bytes 00FE except on last one
                    f.seek(offset)
                    num_records-=1
                    #print "%08X" % offset
                string+=f.read(1)
                bytes_read+=1
                offset+=1
                
            record=string    
            #record = f.read(12)#timestamp plus 4 pods worth of data
            d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1=struct.unpack(">IHHHH",record[:32])
            print "%08X %04X %04X %04X %04X" % (d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1)
            pod_count+=1    
        #print "%08X %04X %04X %04X %04X" % (d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1)

except ValueError:
    print "bad fing appen"
    f.close()
