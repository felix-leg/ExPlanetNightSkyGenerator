#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
from pathlib import Path
APPDIR = Path(__file__).resolve().parent

import data_reader
import rotor
import mover
import mapper

DEFAULT_STAR_NAMES = [
	"Sol",
	"Sirus",
	"Rigil Kentaurus",
	"Polaris", #north star
	"Sig Oct", #south star
	"Procyon",
	"Vega",
	"Rigel",
	"Betelgeuse",
	"Aldebaran",
	"Deneb",
	"Pollux",
	"Fomalhaut",
	"Rastaban",
	"Alpheratz",
	"22Zet Dra", #north Jupiter
	"47Omi Dra", #north Mercury
	"35Eta Oph" #north Uranus
]

def generate(
	stardata,
	central_star,
	axial_tilt,
	inclination,
	lan,
	meridian_angle, #TODO: delete
	eq_long,
	max_mag,
	stars_to_display
):
	"""
	The main function for the program.
	"""
	#moving the stars to the new position and filtering out too dim stars
	try:
		stardata = mover.move_and_filter_stars(stardata, central_star, max_mag)
	except mover.StarNameUnknown as e:
		print(str(e))
		sys.exit(1)
	
	#rotate star data
	rotor.rotate_map(stardata, axial_tilt, inclination, lan, meridian_angle, eq_long)
	
	#make star map
	wide_map, north_map, south_map = mapper.create_maps(stardata, max_mag, stars_to_display)
	return (wide_map, north_map, south_map)

def angle(value):
	if value.endswith("deg"):
		return rotor.deg2rad(float(value[:-3]))
	elif value.endswith("rad"):
		return float(value[:-3])
	else:
		return rotor.deg2rad(float(value)) #default is degrees

if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(allow_abbrev=False, 
		description="A night sky generator for extrasolar planets.",
		epilog="For angle arguments you can specify them either in degrees or radians by adding 'deg' or 'rad' after a number (for example: '20deg' or '0.4rad').")
	parser.add_argument('output', metavar='OUTPUT_FILENAME_PREFIX',
		help="Filename prefix for generated output")
	parser.add_argument('-s', '--star', dest='starname', 
		default='Sol',
		help="Star name of a center star around which the planet orbits (default: %(default)s)")
	parser.add_argument('-a', '--axialtilt', dest='axialtilt', type=angle, 
		default=rotor.EARTH_AXIAL_TILT,
		help="Axial tilt for the planet (default: Earth's axial tilt)")
	parser.add_argument('-i', '--inclination', dest='inclination', type=angle,
		default=0.0,
		help="Inclination for the planet (default: %(default)s)")
	parser.add_argument('-l', '--longitude', dest='lan', type=angle,
		default=0.0, metavar='LONGITUDE_OF_ASCENDING_NODE',
		help="Longitude of ascending node of the planet (default: %(default)s)")
	parser.add_argument('-e', '--meridianangle', dest='meridian_angle', type=angle,
		default=rotor.EARTH_MERIDIAN_ANGLE,
		help="Meridian angle of the planet (default: Earth's meridian angle)")#TODO: delete
	parser.add_argument('-n', '--equatorlongitude', dest='eq_long', type=angle,
		default=0.0,
		help="Ascending node of the planet's equator")
	parser.add_argument('-m', '--magnitude', dest="mag", metavar="MAX_MAGNITUDE", type=float,
		default=6.0,
		help="Specifies the maximal magnitude of visible stars (default: %(default)s)")
	parser.add_argument('-S','--print-stars', dest="printstars", action='store_const',
		const=True, default=False,
		help="Prints star names to the output and exits"
	)
	
	args = parser.parse_args()
	
	stardata = data_reader.loadData(APPDIR / "starMap.data")
	
	if args.printstars:
		if args.output == '-':
			out = sys.stdout
		else:
			out = open(args.output, 'w')
		for star in stardata.values():
			print(", ".join(star.names), file=out)
		out.close()
		sys.exit(0)
	
	wide_map, north_map, south_map = generate(
		stardata,
		args.starname,
		args.axialtilt,
		args.inclination,
		args.lan,
		args.meridian_angle, #TODO: delete
		args.eq_long,
		args.mag,
		DEFAULT_STAR_NAMES
		)
	
	wide_map.save( args.output + '_wide.png' )
	north_map.save( args.output + '_north.png' )
	south_map.save( args.output + '_south.png' )


