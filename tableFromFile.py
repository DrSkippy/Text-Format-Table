#!/usr/bin/env python
__author__ = "Scott Hendrickson"
__version__ = "1.0.1"
__email__ = "scott@drskippy.net"
# Read a comma delimited file and output formatted text table.  Format each number
# to 4 significant figures. E.g.         cat test.csv | ./tableFromFile.py
import csv
import sys
from FormatTable import FormatTable
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-l", "--latex", dest="latex", default=False, action="store_true",
        help="Generate LaTeX table (uses siunitx).")
parser.add_option("-s", "--sig-figs", dest="sf", default=4,
        help="Significant figures (defulat is 4).")
(options, args) = parser.parse_args()
print FormatTable([row for row in csv.reader(sys.stdin)], int(options.sf), options.latex)
