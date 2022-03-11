#!/usr/bin/python
#-*- coding: utf-8 -*-

import struct

class Star:
	"""
	POD class for a star
	"""
	def __init__(self, names, x, y, z, mag, r, g, b):
		self.names = names.split("|")
		self.x = x
		self.y = y
		self.z = z
		self.mag = mag
		self.r = r
		self.g = g
		self.b = b
	
	def __copy__(self):
		return Star("|".join(self.names), self.x, self.y, self.z, self.mag, self.r, self.g, self.b)
	
	def __repr__(self):
		return f"<{self.name}: ({self.x}, {self.y}, {self.z}) mag={self.mag} rgb=({self.r}, {self.g}, {self.b})>"

def loadData(filename):
	data = {}
	with open(filename, 'rb') as i:
		while True:
			r = i.read(4+1)
			if len(r) == 0:
				break
			ID, name_len = struct.unpack(">IB", r)
			name, = struct.unpack(f">{name_len}s", i.read(name_len))
			name = name.decode().strip("\x00")
			
			x, y, z = struct.unpack(">ddd", i.read(8+8+8))
			mag, = struct.unpack(">f", i.read(4))
			r, g, b = struct.unpack(">BBB", i.read(3))
			
			data[ID] = Star(name, x, y, z, mag, r, g, b)
	return data

