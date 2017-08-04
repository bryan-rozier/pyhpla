# -*- coding: utf-8 -*-
"""
Created on Fri Aug 04 16:37:06 2017

PyVCD example

@author: bryan.rozier
"""

import sys

from vcd import VCDWriter

with VCDWriter(sys.stdout, timescale='1 ns', date='today') as writer:
    counter_var = writer.register_var('analyzer', 'counter', 'integer', size=8)
    bit_var = writer.register_var('analyzer','/M1','wire', size=1)
    addr_var = writer.register_var('analyzer','ADDR','wire', size=16)
    for timestamp, value in enumerate(range(10, 20, 2)):
        writer.change(counter_var, timestamp, value)
        writer.change(bit_var, timestamp, value>12)
        writer.change(addr_var, timestamp, value+0xff00)
        