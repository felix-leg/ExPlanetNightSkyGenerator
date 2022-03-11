#!/usr/bin/python
#-*- coding: utf-8 -*-

import PIL.Image
import PIL.ImageDraw
import math

from rotor import deg2rad

IMAGE_HEIGHT = 1024
IMAGE_WIDTH = 2048

CIRCLE_SIZE = 512

GRAY = (64, 64, 64)
GRAY_LIGHT = (128, 128, 128)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

TEXT_COLOR = GREEN

PI_HALF = math.pi / 2.0
PI_DOUBLE = math.pi * 2.0

def calculate_coords(star):
	"""
	Calculates Right Ascesion and Declination
	from the X,Y,Z position of a star
	"""
	
	ra = math.atan2(star.y, star.x)
	dec = math.atan2( star.z, math.sqrt(star.x**2 + star.y**2) )
	return (ra,dec)

def mag2size(mag, max_mag):
	"""
	Calculates size of a dot from star's magnitude
	"""
	size = (max_mag - mag) / max_mag
	size = int(math.log(size * 6))
	if size <= 0:
		size = 1
	return size

def ra_dec_to_pos_rec(ra, dec):
	"""
	Coverts position given in Right Ascesion and Declination
	to the position on the rectangular map
	"""
	y = (dec/PI_HALF) * (IMAGE_HEIGHT/2) + IMAGE_HEIGHT/2
	x = (-ra/PI_DOUBLE * IMAGE_WIDTH) + IMAGE_WIDTH/2
	#if x > IMAGE_WIDTH:
	#	x -= IMAGE_WIDTH
	if x < 0:
		x += IMAGE_WIDTH
	
	return (int(x),IMAGE_HEIGHT - int(y))

def ra_dec_to_polar(ra, dec):
	"""
	Converts position given in Right Ascesion and Declination
	to the position on the polar map
	"""
	radius = (1.0 - math.fabs(dec)/PI_HALF) * CIRCLE_SIZE
	x = math.cos(ra) * radius + CIRCLE_SIZE
	y = math.sin(ra) * radius + CIRCLE_SIZE
	
	return (int(x), int(y))

def create_maps(stardata, max_mag, stars_to_display):
	wide_map = PIL.Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT))
	north_map = PIL.Image.new('RGB', (CIRCLE_SIZE*2, CIRCLE_SIZE*2))
	south_map = PIL.Image.new('RGB', (CIRCLE_SIZE*2, CIRCLE_SIZE*2))
	
	stars_to_display = set(stars_to_display)
	
	#draw coordinate system
	#---	wide map
	wide_draw = PIL.ImageDraw.Draw(wide_map)
	TOP = deg2rad(90)
	BOTTOM = deg2rad(-90)
	for ra in range(0, 360, 30):
		ra = deg2rad(ra)
		wide_draw.line(
			[ra_dec_to_pos_rec(ra, BOTTOM), ra_dec_to_pos_rec(ra, TOP)],
			GRAY,
			1
		)
	RIGHT = deg2rad(180.0)
	LEFT = deg2rad(180.1)
	for dec in range(-90, 90, 30):
		dec = deg2rad(dec)
		wide_draw.line(
			[ra_dec_to_pos_rec(LEFT, dec), ra_dec_to_pos_rec(RIGHT, dec)],
			GRAY,
			1
		)
	wide_draw.line(
		[ra_dec_to_pos_rec(0,BOTTOM), ra_dec_to_pos_rec(0,TOP)],
		GRAY_LIGHT,
		2
	)
	wide_draw.line(
		[ra_dec_to_pos_rec(LEFT,0), ra_dec_to_pos_rec(RIGHT,0)],
		GRAY_LIGHT,
		2
	)
	#---	north map
	north_draw = PIL.ImageDraw.Draw(north_map)
	for dec in range(0, 90, 15):
		x, y = ra_dec_to_polar(0, deg2rad(dec))
		size = x - CIRCLE_SIZE
		north_draw.ellipse((CIRCLE_SIZE-size,CIRCLE_SIZE-size, CIRCLE_SIZE+size, CIRCLE_SIZE+size),
			outline=GRAY,
			fill=None,
			width=1
		)
	for ra in range(0, 360, 30):
		x, y = ra_dec_to_polar(deg2rad(ra), 0)
		north_draw.line((CIRCLE_SIZE, CIRCLE_SIZE, x, y),
			fill=GRAY,
			width=1
		)
	x, y = ra_dec_to_polar(0,0)
	north_draw.line((CIRCLE_SIZE, CIRCLE_SIZE, x, y), fill=GRAY_LIGHT, width=2)
	#---	south map
	south_draw = PIL.ImageDraw.Draw(south_map)
	for dec in range(0, 90, 15):
		x, y = ra_dec_to_polar(0, deg2rad(dec))
		size = x - CIRCLE_SIZE
		south_draw.ellipse((CIRCLE_SIZE-size,CIRCLE_SIZE-size, CIRCLE_SIZE+size, CIRCLE_SIZE+size),
			outline=GRAY,
			fill=None,
			width=1
		)
	for ra in range(0, 360, 30):
		x, y = ra_dec_to_polar(deg2rad(ra), 0)
		south_draw.line((CIRCLE_SIZE, CIRCLE_SIZE, x, y),
			fill=GRAY,
			width=1
		)
	x, y = ra_dec_to_polar(0,0)
	south_draw.line((CIRCLE_SIZE, CIRCLE_SIZE, x, y), fill=GRAY_LIGHT, width=2)
	
	wide_text = []
	north_text = []
	south_text = []
	#calculate positions and draw stars
	for star in stardata.values():
		ra, dec = calculate_coords(star)
		color = (star.r, star.g, star.b)
		size = mag2size( star.mag, max_mag )
		draw_name = not stars_to_display.isdisjoint(set(star.names))
		#wide map
		x, y = ra_dec_to_pos_rec(ra, dec)
		wide_draw.ellipse((x-size,y-size, x+size,y+size), fill=color)
		if draw_name:
			wide_text.append(((x,y), star.names[0]))
		#polar map
		if dec < 0:
			polar_draw = south_draw
			polar_text = south_text
		else:
			polar_draw = north_draw
			polar_text = north_text
		x, y = ra_dec_to_polar(ra, dec)
		polar_draw.ellipse((x-size,y-size, x+size,y+size), fill=color)
		if draw_name:
			polar_text.append(((x,y), star.names[0]))
	
	#draw texts
	for pos, text in wide_text:
		wide_draw.text(pos, text, fill=TEXT_COLOR)
	for pos, text in north_text:
		north_draw.text(pos, text, fill=TEXT_COLOR)
	for pos, text in south_text:
		south_draw.text(pos, text, fill=TEXT_COLOR)
	
	return (wide_map, north_map, south_map)



