#!/usr/bin/python
#-*- coding: utf-8 -*-

import math

class StarNameUnknown(Exception):
	
	def __init__(self, name, *args, **kwargs):
		self.starname = name
		super().__init__(self, *args, **kwargs)
	
	def __str__(self):
		return f"Unknown star name: {self.starname}"



def move_and_filter_stars(stardata, central_star, max_magnitude):
	#find the central star
	center = None
	centerID = None
	for ID, star in stardata.items():
		if central_star in star.names:
			center = star
			centerID = ID
			break
	if center is None:
		raise StarNameUnknown(central_star)
	
	#move and filter stars
	stars = {}
	for ID, star in stardata.items():
		if ID == centerID:
			continue
		new_x = star.x - center.x
		new_y = star.y - center.y
		new_z = star.z - center.z
		distance = math.sqrt( new_x**2 + new_y**2 + new_z**2 )
		app_mag = (5 * math.log10(distance / 10)) + star.mag
		if app_mag > max_magnitude:
			continue
		star.x = new_x
		star.y = new_y
		star.z = new_z
		star.mag = app_mag
		stars[ID] = star
	
	return stars



