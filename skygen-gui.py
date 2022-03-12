#!/usr/bin/python3
#-*- coding: utf-8 -*-

import gi, copy
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib

#local import
import data_reader
import rotor
import mover
import mapper

from pathlib import Path
APPDIR = Path(__file__).resolve().parent

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
	"Alpheratz"
]

class MainWindow(Gtk.Window):
	def __init__(self):
		super().__init__(title="SkyGen GUI")
		self.connect("destroy", Gtk.main_quit)
		
		box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
		self.add(box)
		
		#menu
		menuBar = Gtk.MenuBar()
		box.pack_start(menuBar, True, False, 0)
		menuButton = Gtk.MenuItem(label="Menu")
		menuBar.append(menuButton)
		menu = Gtk.Menu()
		menuButton.set_submenu(menu)
		
		chooseStarMenu = Gtk.MenuItem(label="Choose star")
		menu.append(chooseStarMenu)
		chooseStarMenu.connect("activate", self.changeStar)
		
		seeNorth = Gtk.RadioMenuItem(label="See north map", active=True)
		menu.append(seeNorth)
		seeSouth = Gtk.RadioMenuItem(label="See south map")
		menu.append(seeSouth)
		seeWide = Gtk.RadioMenuItem(label="See wide map")
		menu.append(seeWide)
		seeSouth.join_group(seeNorth)
		seeWide.join_group(seeNorth)
		
		seeNorth.connect("toggled", self.switchMap, "north")
		seeSouth.connect("toggled", self.switchMap, "south")
		seeWide.connect("toggled", self.switchMap, "wide")
		
		#main image
		self.skyImage = Gtk.Image()
		box.pack_start(self.skyImage, True, True, 0)
		
		#param fields
		grid = Gtk.Grid(column_spacing=10, row_spacing=10)
		box.pack_start(grid, False, False, 0)
		
		grid.attach(Gtk.Label(label="Axial tilt"), 0, 0, 1, 1)
		grid.attach(DegEdit(self.axialTiltChanged, 23.4392811), 0, 1, 1, 1)
		
		grid.attach(Gtk.Label(label="Inclination"), 1, 0, 1, 1)
		grid.attach(DegEdit(self.incChanged), 1, 1, 1, 1)
		
		grid.attach(Gtk.Label(label="Longitude of ascending node"), 0, 2, 1, 1)
		grid.attach(DegEdit(self.lanChanged), 0, 3, 1, 1)
		
		grid.attach(Gtk.Label(label="Equator ascending node"), 1, 2, 1, 1)
		grid.attach(DegEdit(self.eqLanChanged), 1, 3, 1, 1)
		
		self.show_all()
		
		#data
		self.axis = rotor.deg2rad(23.4392811)
		self.inc = 0.0
		self.lan = 0.0
		self.eq = 0.0
		self.map = "north"
		self.stardata = data_reader.loadData(APPDIR / "starMap.data")
		self.stardata = mover.move_and_filter_stars(self.stardata, "Sol", 6.0)
		
		self.updateImage()
	
	def axialTiltChanged(self, val):
		self.axis = rotor.deg2rad(val)
		self.updateImage()
	
	def incChanged(self, val):
		self.inc = rotor.deg2rad(val)
		self.updateImage()
	
	def lanChanged(self, val):
		self.lan = rotor.deg2rad(val)
		self.updateImage()
	
	def eqLanChanged(self, val):
		self.eq = rotor.deg2rad(val)
		self.updateImage()
	
	def changeStar(self, *args):
		dialog = Gtk.MessageDialog(
			parent=self,
			destroy_with_parent=True,
			message_type=Gtk.MessageType.QUESTION,
			buttons=Gtk.ButtonsType.OK_CANCEL,
			text="Select star",
			secondary_text="Choose the central star"
		)
		starEntry = Gtk.Entry()
		dialog.get_content_area().pack_start(starEntry, True, True, 0)
		starEntry.show()
		
		if dialog.run() == Gtk.ResponseType.OK:
			starName = starEntry.get_text().strip()
			if len(starName) > 0:
				try:
					stardata = data_reader.loadData(APPDIR / "starMap.data")
					self.stardata = mover.move_and_filter_stars(stardata, starName, 6.0)
					self.updateImage()
				except mover.StarNameUnknown:
					errorDialog = Gtk.MessageDialog(
						parent=self,
						modal=True,
						message_type=Gtk.MessageType.ERROR,
						buttons=Gtk.ButtonsType.OK,
						text=f"There is no star named: {starName}"
					)
					errorDialog.run()
					errorDialog.destroy()
		
		dialog.destroy()
	
	def switchMap(self, radio, value):
		if radio.get_active():
			self.map = value
			self.updateImage()
	
	def updateImage(self):
		#calculate
		stardata = copy.deepcopy(self.stardata)
		rotor.rotate_map(stardata, self.axis, self.inc, self.lan, self.eq)
		wide_map, north_map, south_map = mapper.create_maps(stardata, 6.0, DEFAULT_STAR_NAMES)
		
		#select map
		if self.map == "north":
			north_map.thumbnail((700,700))
			the_map = north_map
		elif self.map == "south":
			south_map.thumbnail((700,700))
			the_map = south_map
		elif self.map == "wide":
			wide_map.thumbnail((1400, 700))
			the_map = wide_map
		
		#convert to pixbuf
		imData = the_map.tobytes()
		w, h = the_map.size
		imData = GLib.Bytes(imData)
		pix = GdkPixbuf.Pixbuf.new_from_bytes(imData, GdkPixbuf.Colorspace.RGB, 
			False, 8, w, h, w * 3)
		
		#load to image
		self.skyImage.set_from_pixbuf(pix)

class DegEdit(Gtk.Box):
	def __init__(self, update_function, init_deg=0.0):
		super().__init__(spacing=0, orientation=Gtk.Orientation.HORIZONTAL)
		self.onUpdate = update_function
		
		self.downByDotZeroOne = Gtk.Button(label="<")
		self.pack_start(self.downByDotZeroOne, False, False, 0)
		self.downByDotZeroOne.connect("clicked", self.updateValue, -0.01)
		
		self.downByDotOne = Gtk.Button(label="<<")
		self.pack_start(self.downByDotOne, False, False, 0)
		self.downByDotOne.connect("clicked", self.updateValue, -0.1)
		
		self.downByOne = Gtk.Button(label="<<<")
		self.pack_start(self.downByOne, False, False, 0)
		self.downByOne.connect("clicked", self.updateValue, -1.0)
		
		self.editField = Gtk.Entry(text=str(init_deg))
		self.pack_start(self.editField, True, True, 0)
		self.editField.connect("changed", self.valueUpdated)
		
		self.upByOne = Gtk.Button(label=">>>")
		self.pack_start(self.upByOne, False, False, 0)
		self.upByOne.connect("clicked", self.updateValue, 1.0)
		
		self.upByDotOne = Gtk.Button(label=">>")
		self.pack_start(self.upByDotOne, False, False, 0)
		self.upByDotOne.connect("clicked", self.updateValue, 0.1)
		
		self.upByDotZeroOne = Gtk.Button(label=">")
		self.pack_start(self.upByDotZeroOne, False, False, 0)
		self.upByDotZeroOne.connect("clicked", self.updateValue, 0.01)
	
	def updateValue(self, source, shift):
		val = float( self.editField.get_text() )
		val += shift
		self.editField.set_text( str(val) )
	
	def valueUpdated(self, *args):
		try:
			val = float( self.editField.get_text() )
		except ValueError:
			val = 0.0
		self.onUpdate(val)

if __name__ == "__main__":
	win = MainWindow()
	Gtk.main()

