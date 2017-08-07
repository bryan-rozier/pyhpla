# pyhpla
Python Tools to aid talking to HP16000 Logic Analyser card e.g HP16555A
These assume the LA card is in a HP16500C chassis

VCD_example.py will process the ascii format files downloaded from a HP16555A 
card and write a VCD format file to stdout. The VCD file can be viewed using 
GTKWave. This assumes all data is hex which works for hex variables and 
single bit binary data. Other formats not supported.

It assumes the LA is in slot D and the data is from LA Machine1 running in 
timing mode, I get this data via ftp, hence the data will be in 
$pwd\slot_d\data.asc\machine1\

It will add all files the above directory to the VCD file except the the 
following:-
1st_line.txt - ignored
line_num.txt - ignored
time_abs.txt - timestamp assumed this is nanoseconds. 
               Don't think VCD can cope with negative time stamps so VCD is 
               relative to first sample.
example of use:
python VCD_example.py > fred.vcd

TODO: need to make path and machine name command line options.

GTKWave viewer:

  http://gtkwave.sourceforge.net

It relies on the following packages 

pyvcd package:

  https://github.com/SanDisk-Open-Source/pyvcd


