import configparser
import pygame
from math import floor

class Level:
	def __init__(self, filename):
		self.map = []
		self.key = {}
		parser   = configparser.ConfigParser()
		parser.read(filename)
		self.tileset = parser.get("level","tileset")
		self.map     = parser.get("level","map").split("\n")
		self.tile_width   = int(parser.get("level","width"))
		self.tile_height  = int(parser.get("level","height"))
		self.tiles   = self.load_tile_table(self.tileset,self.tile_width,self.tile_height)
		for section in parser.sections():
			if len(section) == 1:
				self.key[section] = dict(parser.items(section))
		self.width = len(self.map[0])
		self.height = len(self.map)
	
	def get_tile(self,x,y):
		try:
			char = self.map[y][x]
		except IndexError:
			return {}

		try:
			return self.key[char]
		except KeyError:
			return {}
	
	def render(self,screen,width,height):
		sc_width = screen.get_rect().width
		sc_height = screen.get_rect().height

		tile_width = int(sc_width / width)
		tile_height = int(sc_height / height)

		image = pygame.Surface((self.width*tile_width,self.height*tile_height))

		for i in range(0,self.width):
			for j in range(0,self.height):
				s = self.get_tile(i,j)['tile'].split(',')
				ty = int(s[0])
				tx = int(s[1])
				surf = self.tiles[tx][ty]
				surf = pygame.transform.smoothscale(surf, (tile_width,tile_height))
				image.blit(surf,(i*tile_width,j*tile_height))
		return image



	def load_tile_table(self,filename,width,height):
		image = pygame.image.load(filename).convert()
		image_width, image_height = image.get_size()
		tile_table = []
		for tile_x in range(0, floor(image_width/width)):
			line = []
			tile_table.append(line)
			for tile_y in range(0, floor(image_height/height)):
				rect = (tile_x*width, tile_y*height, width, height)
				line.append(image.subsurface(rect))
		return tile_table


