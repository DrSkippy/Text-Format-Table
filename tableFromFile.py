#!/usr/bin/env python
#
__copyright__ = "Copyright 2011 Scott Hendrickson"
__license__ = "GPL"
__author__ = "Scott Hendrickson"
__version__ = "1.0.0"
__email__ = "scott@drskippy.net"
#
# Read a comma delimited file and output formatted text table.  Format each number
# to 4 significant figures.
#
# For example: 
#    cat test.csv | ./tableFromFile.py
#
import csv
import sys
from FormatTable import FormatTable

arry = []
for row in csv.reader(sys.stdin):
	r = [float(x) for x in row]
	arry.append(r)

ft = FormatTable(arry, 4)
print ft
