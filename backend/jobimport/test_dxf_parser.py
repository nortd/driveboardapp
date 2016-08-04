#!/usr/bin/python

import io

from dxf_parser import DXFParser

tolerance = 0.08
preColor = {}
postColor = {}

fin = open("test.dxf"); 
dxf_string = fin.read();  
fin.close() 

dxf_string = unicode(dxf_string)
dxfParser = DXFParser(0.8)
forced_unit = 0

parse_results = dxfParser.parse(dxf_string, forced_unit)

#print "parsed results: ", parse_results    

