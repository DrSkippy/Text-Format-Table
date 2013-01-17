#!/usr/bin/env python
__author__ = "Scott Hendrickson"
__email__ = "scott@drskippy.net"
# Read a comma delimited file and output formatted text table.
# Assumes header row is first
import csv
import fileinput
from FormatTable import FormatTable
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-l", "--latex", dest="latex", default=False, action="store_true",
        help="Generate LaTeX table (uses siunitx).")
parser.add_option("-s", "--sig-figs", dest="sf", default=None,
        help="Significant figures (default is 4).")
parser.add_option("-c", "--sig-figs-by-column", dest="sflist", default=None,
        help='Significant figures by column as list e.g. "[1,2,2,2,4]"')
(options, args) = parser.parse_args()
if options.sf is None and options.sflist is None:
    options.sf = 4
print FormatTable([row for row in csv.reader(fileinput.input(args))], options.sf, options.latex, options.sflist)
