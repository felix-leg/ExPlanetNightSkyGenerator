#!/usr/bin/python
#-*- coding: utf-8 -*-

import math

def deg2rad(d):
	return (d/180.0) * math.pi

EARTH_AXIAL_TILT = deg2rad(-23.4392811)
EARTH_MERIDIAN_ANGLE = deg2rad(280.147) #TODO: delete

#---------------------------
class Rotor:
	def __init__(self, deg=0.0, x=0.0, y=0.0, z=0.0, direct=False):
		if direct:
			self.a = deg
			self.x = x
			self.y = y
			self.z = z
		else:
			self.a = math.cos( deg/2.0 )
			sinD = math.sin( deg/2.0 )
			self.x = sinD * x
			self.y = sinD * y
			self.z = sinD * z
	
	def __repr__(self):
		return f"<Rotor: a={self.a} x={self.x} y={self.y} z={self.z}>"
	
	def mul_by_rotor(self, other):
		newA = self.a * other.a - self.x * other.x - self.y * other.y - self.z * other.z
		newX = self.x * other.a + other.x * self.a + self.y * other.z - self.z * other.y
		newY = self.y * other.a + other.y * self.a + self.z * other.x - self.x * other.z
		newZ = self.z * other.a + other.z * self.a + self.x * other.y - self.y * other.x
		
		return Rotor(newA, newX, newY, newZ, True)
	
	def reverse(self):
		return Rotor(self.a, -self.x, -self.y, -self.z, True)
	
	def rotVec(self, x, y, z):
		p = Rotor(0, x, y, z, True)
		r = self.mul_by_rotor( p ).mul_by_rotor( self.reverse() )
		
		return (r.x, r.y, r.z)

def rotX(rotor, deg):
	return rotor.mul_by_rotor( Rotor(deg, 1, 0, 0) )

def rotY(rotor, deg):
	return rotor.mul_by_rotor( Rotor(deg, 0, 1, 0) )

def rotZ(rotor, deg):
	return rotor.mul_by_rotor( Rotor(deg, 0, 0, 1) )

def rotRotor(rotor, another):
	return rotor.mul_by_rotor( another )

#---------------------------

def make_rotation(axial_tilt, inclination, lan, meridian_angle, eq_long):
	
	planetRotor = Rotor()
	
	planetRotor = rotX(planetRotor, -EARTH_AXIAL_TILT)
	#planetRotor = rotZ(planetRotor, meridian_angle - EARTH_MERIDIAN_ANGLE) #TODO: delete
	
	equatorRotor = Rotor(eq_long, 0, 0, 1)
	eqAxis = equatorRotor.rotVec(1,0,0)
	planetRotor = rotRotor(planetRotor, Rotor(axial_tilt, *eqAxis))
	
	orbitRotor = Rotor(lan, 0, 0, 1)
	#orbitRotor = rotZ( orbitRotor, lan )
	lanAxis = orbitRotor.rotVec(1,0,0)
	planetRotor = rotRotor(planetRotor, Rotor(inclination, *lanAxis))
	
	return planetRotor

def rotate_map(stardata, axial_tilt, inclination, lan, meridian_angle, eq_long):
	"""
	Main function in this module
	"""
	rot = make_rotation(axial_tilt, inclination, lan, meridian_angle, eq_long)
	
	for star in stardata.values():
		star.x, star.y, star.z = rot.rotVec(star.x, star.y, star.z)

