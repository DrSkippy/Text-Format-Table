#!/usr/bin/env python
__copyright__ = "Copyright 2011 Scott Hendrickson"
__license__ = "GPL"
__author__ = "Scott Hendrickson"
__version__ = "1.0.0"
__email__ = "scott@drskippy.net"

import sys
import math
import string

class FNumber(object):
    """Float number container produces string formatted number representation with 
    specified number of significant figures, "," separators for thousands and " "
    separators for thousanths.  Provides access to string size and offset to 
    decimal.
    """

    # customize separators if necessary
    intSeparator = ","
    mantissaSeparator = " "
    decimalSeparator = "."

    def __init__(self, xstring, sf, latex=False):
        try:
            x = float(xstring)
            if math.isnan(x) or math.isinf(x):
                raise ValueError
            if sf <= 0:
                print >>sys.stderr, "What does 0 significant figures mean?"
                sys.exit()
        except ValueError:
            # string
            self.sigFigs = 0
            self.value = 0.0
            self.sign = ""
            self.sigValue = 0.0
            if latex:
                self.valueStr = "{%s}"%xstring
            else:
                self.valueStr = xstring
        else:   
            # store the values
            self.sigFigs = int(sf)
            self.value = float(x)
            # set the sign
            if self.value < 0:
                self.sign = "-"
            else:
                self.sign = ""
            # calculate the value to desire sig figs
            if x <> 0:
                decade = int(math.floor(math.log10(abs(x))))
                decadeFactor = math.pow(10., self.sigFigs - decade - 1)
                self.sigValue = round(float(abs(x)) * decadeFactor, 0) / decadeFactor
            else:
                decade = 0
                decadeFactor = 1
                self.sigValue = 0.0
            # are any of the digits in int portion significant?
            if decade > 0:
                intSize = decade + 1
            else: # decade <= 0
                intSize = 0
            #
            if intSize > 0:  # at least on sig digit left of decimal
                if intSize >= self.sigFigs:
                    mantissaSize = 0
                else:
                    mantissaSize = self.sigFigs - intSize
            else: # intSize == 0
                mantissaSize = self.sigFigs - decade - 1
            #
            fmtStr = "%%%d.%dF"%(intSize, mantissaSize)
            tmpStr = fmtStr%self.sigValue
            tmpList = tmpStr.split(self.decimalSeparator)
            intStr = self.sign
            intLen = len(tmpList[0])
            for i in range(0, intLen):
                if (intLen - i)%3 == 0 and i <> 0:
                    intStr += self.intSeparator
                intStr += tmpList[0][i]
            mantStr = self.decimalSeparator
            for i in range(0, mantissaSize):
                if i <> 0 and i%3 == 0 and i <> mantissaSize:
                    mantStr += self.mantissaSeparator
                mantStr += tmpList[1][i]
            self.valueStr = intStr + mantStr
            if latex:
                self.valueStr = self.valueStr.replace(",","")
    
    def size(self):
        return len(self.valueStr)

    def getOffset(self):
        # count, not index
        if self.sigFigs != 0:
            res = 1 + string.index(self.valueStr, self.decimalSeparator)
        else:
            res = 1 + self.size()/2
        return res
    
    def getRightOffset(self):
        return self.size() - self.getOffset()

    def getPadded(self, width, offset):
        left = offset - self.getOffset()
        right = width - left - self.size()
        if left < 0 or right < 0:
            print >>sys.stderr, "Check you column width and offset. Aborting!"
        return " "*left + self.valueStr + " "*right
    
    def __repr__(self):
        return self.valueStr
            
if __name__ == '__main__':
    """Simple example of a single column of numbers, aligned on the decimal points"""
    values = [ 
            (1234.234, 1),
            (1234.234, 2),
            (1234.234, 3),
            (123.234, 3),
            (123.234, 4),
            (1234.234, 4),
            (1234.234, 5),
            (-1234.234, 5),
            (1234.234, 6),
            (1234.234, 7),
            (1234.234, 9),
            (.23456789, 1),
            (.23456789, 2),
            ("hello there", 0),
            (-.23456789, 2),
            (.23456789, 3),
            (.23456789, 4),
            (.23456789, 5),
            (.0023456789, 3),
            (.00023456789, 4),
            (.000023456789, 5),
            (23456789, 2),
            (23456789, 4),
            (23456789, 6),
            (-23456789, 6),
            (23456789.123345, 8),
            (23456789.123345, 11),
            (1234.234, 0)
        ]
    for f in values:
        a = FNumber(f[0], f[1])
        #print str(f), a.sigValue, a.size(), a.getOffset(), a
        print a.getPadded(30, 15)
