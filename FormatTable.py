#!/usr/bin/env python
#
__copyright__ = "Copyright 2011 Scott Hendrickson"
__license__ = "GPL"
__author__ = "Scott Hendrickson"
__version__ = "1.0.0"
__email__ = "scott@drskippy.net"
#
#
import csv
import sys
from FNumber import FNumber

class Offsets(object):
	""" Simple container for column alignement offset information.  "test" each
	number in the column and this object will return the column width and 
	decimal offset required to accomodate all the numbers. """

	def __init__(self):
		self.right = []
		self.left = []
	
	def test(self, column, left, right):
		if column > len(self.left) - 1:
			self.left.append(0)
			self.right.append(0)
		if self.left[column] < left:
			self.left[column] = left
		if self.right[column] < right:
			self.right[column] = right
	def getRight(self, c):
		return self.right[c]

	def getLeft(self, c):
		return self.left[c]

	def size(self, c):
		return self.right[c] + self.left[c]

class FormatTable(object):
	""" Create a text table of decimal aligned numbers formated with FNumber. """
	
	# customize table column separator as needed
	tableSeparator = " | "

	def __init__(self, table, sf=None):
		self.offsets = Offsets()
		self.cnums = []
		for row in table:
			if sf is None:
				# if sf=None, then each number is a tuple with the second element
				# containing the sf to use for that number
				tmp = [ FNumber(x, s) for (x,s) in row]
			else:
				# All numbers in the table use the same sf
				tmp = [ FNumber(x, sf) for x in row]
			self.cnums.append(tmp)
			for i in range(0,len(tmp)):
				self.offsets.test(i, tmp[i].getOffset(), tmp[i].getRightOffset())

	def __repr__(self):
		res = ""
		for row in self.cnums:
			tmp = []
			for i in range(0,len(row)):
				tmp.append( row[i].getPadded(self.offsets.size(i), self.offsets.getLeft(i)) )
			res += self.tableSeparator.join(tmp)
			res += "\n"
		return res
			
if __name__ == '__main__':
	""" Simple example of multi-column table with varying sf specified for each number. """
	values = [ [
			(1234.234, 1),
			(1234.234, 2),
			(1234.234, 3),
			(123.234, 3)],[
			(123.234, 4),
			(1234.234, 1),
			(123.234, 4),
			(1234.234, 4)],[
			(1234.234, 5),
			(-1234.234, 5),
			(1234.234, 6),
			(1234.234, 7)],[
			(1234.234, 9),
			(.23456789, 1),
			(.23456789, 2),
			(-.23456789, 2)],[
			(.23456789, 3),
			(.23456789, 4),
			(.23456789, 5),
			(.0023456789, 3)],[
			(.00023456789, 4),
			(.000023456789, 5),
			(23456789, 2),
			(23456789, 4)],[
			(23456789, 6),
			(-23456789, 6),
			(23456789.123345, 8),
			(23456789.123345, 15)
		] ]
	ft = FormatTable(values)
	print ft
	print "*****\n"
	# ...and same numbers with constant sf for the whole table
	arry = []
	for v in values:
		tmp = [x[0] for x in v]
		arry.append(tmp)
	f1 = FormatTable (arry, 3)
	print f1
