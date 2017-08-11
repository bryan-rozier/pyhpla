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
        p_InstrumentID,p_RevisionCode,p_NumAcqChips,p_AnalyzerID=struct.unpack(">IIII",record[0x36:0x36+16])
        if p_InstrumentID==16500:#as its on a HP16500C
                print "Found p_InstrumentID:%d" % p_InstrumentID
                print "p_RevisionCode  %08X" % p_RevisionCode
                print "p_NumAcqChips  %08X"% p_NumAcqChips
                print "p_AnalyzerID  %s"% dict_AnalyzerID[p_AnalyzerID]
        #Offset 0x46 is 70bytes data for Analyzer1
        p_MachineDataMode,p_PodList,p_MasterChip,p_MemDepth,p_unused1,p_SamplePeriod_ps,p_TagType,p_TriggerOffset,p_unused2=struct.unpack(">iIIIIQIQ30s",record[0x36+16:0x36+16+70])
        if p_MachineDataMode!=-1:#Machine is active
                print "p_MachineDataMode  %s"% dict_MachineDataMode[p_MachineDataMode]
                print "p_PodList  %08X"% p_PodList
                pl_bitmask=int('00000001',2)
                for pod in range (1,12):# pod1 is bit1 (not bit0)
                    if ((pl_bitmask<<pod) & p_PodList):
                        print "pod%d" % pod
                if ((pl_bitmask<<21) & p_PodList):#only one embedded clock pod
                        print "clkpod1"
                print "p_MasterChip  %08X"% p_MasterChip
                print "p_MemDepth  %08X"% p_MemDepth
                print "p_SamplePeriod_ps  %016X (%d pS)"% (p_SamplePeriod_ps,p_SamplePeriod_ps)
                print "p_TagType  %s"% dict_TagType[p_TagType]
                print "p_TriggerOffset  %016X" % p_TriggerOffset
        #Offset 0x8C is another 70bytes of above data repeated (must be missing some bits???) for Analyzer2
        p_MachineDataMode2,p_PodList2,p_MasterChip2,p_MemDepth2,p_unused21,p_SamplePeriod_ps2,p_TagType2,p_TriggerOffset2,p_unused22=struct.unpack(">iIIIIQIQ30s",record[0x8C:0x8C+70])
        if p_MachineDataMode2!=-1:#Machine is active
                print "p_MachineDataMode2  %s"% dict_MachineDataMode[p_MachineDataMode2]
                print "p_PodList2  %08X"% p_PodList2
                pl_bitmask=int('00000001',2)
                for pod in range (1,12):# pod1 is bit1 (not bit0)
                    if ((pl_bitmask<<pod) & p_PodList2):
                        print "pod%d" % pod
                if ((pl_bitmask<<21) & p_PodList2):#only one embedded clock pod
                        print "clkpod1"
                print "p_MasterChip2  %08X"% p_MasterChip2
                print "p_MemDepth2  %08X"% p_MemDepth2
                print "p_SamplePeriod_ps2  %016X (%d pS)"% (p_SamplePeriod_ps2,p_SamplePeriod_ps2)
                print "p_TagType2  %s"% dict_TagType[p_TagType2]
                print "p_TriggerOffset2  %016X" % p_TriggerOffset2
        #Offset 0xD2 unused
        #Offset 0XFA is count of rows of valid data for each pod
        p_card3_pod4_valid_rows,p_card3_pod3_valid_rows_hi=struct.unpack(">IH",record[0xFA:0xFA+6])# last thing in this 256 byte block
        # Next block
        f.seek(0x300)
        record = f.read(256)
        r_marker,p_card3_pod3_valid_rows_lo,p_card3_pod2_valid_rows,p_card3_pod1_valid_rows=struct.unpack(">HHII",record[0x00:0x00+12])
        print "next block"
        if r_marker==0x00FE:
            p_card3_pod3_valid_rows=p_card3_pod3_valid_rows_lo + (p_card3_pod3_valid_rows_hi<<8)
            print "p_card3_pod4_valid_rows %08X"% p_card3_pod4_valid_rows
            print "p_card3_pod3_valid_rows %08X"% p_card3_pod3_valid_rows
            print "p_card3_pod2_valid_rows %08X"% p_card3_pod2_valid_rows
            print "p_card3_pod1_valid_rows %08X"% p_card3_pod1_valid_rows
        p_card2_pod4_valid_rows,p_card2_pod3_valid_rows,p_card2_pod2_valid_rows,p_card2_pod1_valid_rows=struct.unpack(">IIII",record[0x0C:0x0C+16])
        print "p_card2_pod4_valid_rows %08X"% p_card2_pod4_valid_rows
        print "p_card2_pod3_valid_rows %08X"% p_card2_pod3_valid_rows
        print "p_card2_pod2_valid_rows %08X"% p_card2_pod2_valid_rows
        print "p_card2_pod1_valid_rows %08X"% p_card2_pod1_valid_rows
        p_card1_pod4_valid_rows,p_card1_pod3_valid_rows,p_card1_pod2_valid_rows,p_card1_pod1_valid_rows=struct.unpack(">IIII",record[0X1C:0X1C+16])
        print "p_card1_pod4_valid_rows %08X"% p_card1_pod4_valid_rows
        print "p_card1_pod3_valid_rows %08X"% p_card1_pod3_valid_rows
        print "p_card1_pod2_valid_rows %08X"% p_card1_pod2_valid_rows
        print "p_card1_pod1_valid_rows %08X"% p_card1_pod1_valid_rows
        #Offset 0x2c Unused (40 Bytes)
        # trigger point
        p_card3_pod4_trigger_marker,p_card3_pod3_trigger_marker,p_card3_pod2_trigger_marker,p_card3_pod1_trigger_marker=struct.unpack(">IIII",record[0x54:0x54+16])
        print "p_card3_pod4_trigger_marker %08X"% p_card3_pod4_trigger_marker
        print "p_card3_pod3_trigger_marker %08X"% p_card3_pod3_trigger_marker
        print "p_card3_pod2_trigger_marker %08X"% p_card3_pod2_trigger_marker
        print "p_card3_pod1_trigger_marker %08X"% p_card3_pod1_trigger_marker
        p_card2_pod4_trigger_marker,p_card2_pod3_trigger_marker,p_card2_pod2_trigger_marker,p_card2_pod1_trigger_marker=struct.unpack(">IIII",record[0x64:0x64+16])
        print "p_card2_pod4_trigger_marker %08X"% p_card2_pod4_trigger_marker
        print "p_card2_pod3_trigger_marker %08X"% p_card2_pod3_trigger_marker
        print "p_card2_pod2_trigger_marker %08X"% p_card2_pod2_trigger_marker
        print "p_card2_pod1_trigger_marker %08X"% p_card2_pod1_trigger_marker
        p_card1_pod4_trigger_marker,p_card1_pod3_trigger_marker,p_card1_pod2_trigger_marker,p_card1_pod1_trigger_marker=struct.unpack(">IIII",record[0x74:0x74+16])
        print "p_card1_pod4_trigger_marker %08X"% p_card1_pod4_trigger_marker
        print "p_card1_pod3_trigger_marker %08X"% p_card1_pod3_trigger_marker
        print "p_card1_pod2_trigger_marker %08X"% p_card1_pod2_trigger_marker
        print "p_card1_pod1_trigger_marker %08X"% p_card1_pod1_trigger_marker
        
        #Time
        f.seek(0x400)
        record = f.read(256)
        # Date/Time at 0x470
        p_year,p_month,p_day,p_weekday,p_hour,p_min,p_secs=struct.unpack(">HBBBBBB",record[0x70:0x70+8])
        dict_weekday = {1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",5:"Friday",6:"Saturday",7:"Sunday"}
        print "%d/%d/%d %s %d:%d:%d"% (p_day, p_month, p_year+1990,dict_weekday[p_weekday],p_hour,p_min,p_secs)
        #read first partial 'data' record
        offset=0x478
        f.seek(offset)
        num_records-=2# data starts in 3rd record I think
        pod_count=0
        print "C pod4 pod3 pod2 pod1"
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
            d_clock,d_pod4,d_pod3,d_pod2,d_pod1=struct.unpack(">IHHHH",record[:32])
            # assume only 1 board therefore only one clock pod ????
            d_clock&=0xf
            print "%01X %04X %04X %04X %04X" % (d_clock,d_pod4,d_pod3,d_pod2,d_pod1)
            pod_count+=1    
        #print "%08X %04X %04X %04X %04X" % (d_timestamp,d_pod4,d_pod3,d_pod2,d_pod1)

except ValueError:
    print "bad fing appen"
    f.close()
