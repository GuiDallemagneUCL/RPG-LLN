import numpy
import pygame

class Person:
	def __init__(self,sprites_filename,map_pos,grid,direction):
		self.grid = grid
		self.map_pos = map_pos
		self.set_pos(map_pos)
		self.sprites = self.set_sprites(sprites_filename)
		self.direction = direction
		self.speed = 4
	
	def set_pos(self,map_pos):
		self.pos = tuple(numpy.multiply(self.grid.tilesize,map_pos))

	def set_sprites(self,filename):
		image = pygame.image.load(filename).convert_alpha()
		image_width, image_height = image.get_size()
		sprites = []
		for x in range(0,12):
			rect = (int(image_width/12)*x,0,int(image_width/12),image_height)
			surf = pygame.transform.smoothscale(image.subsurface(rect),tuple([int(el) for el in self.grid.tilesize]))
			sprites.append(surf)

		return sprites

	def blit(self,screen,n):
		screen.blit(self.sprites[n],tuple(numpy.add(self.grid.view_coord,self.pos)))


class Player(Person):
	def __init__(self,sprites_filename,map_pos,grid,direction):
		Person.__init__(self,sprites_filename,map_pos,grid,direction)
		self.grid.view_coord = (-self.pos[0]+int(self.grid.size[0]/2)*self.grid.tilesize[0],-self.pos[1]+int(self.grid.size[1]/2)*self.grid.tilesize[1])
		self.pos = (int(self.grid.size[0]/2)*self.grid.tilesize[0],int(self.grid.size[1]/2)*self.grid.tilesize[1])
		print(self.pos)

	def blit(self,screen,n):
		screen.blit(self.sprites[n],self.pos)

	def movement(self,current_direction):
		if sum(current_direction) != 0:
			mindir = 1e6
			curdir = 0
			for i in range(0,len(current_direction)):
				if current_direction[i] != 0 and current_direction[i] < mindir:
					mindir = current_direction[i]
					curdir = i
			self.direction = curdir
			mod = self.grid.getMod()
			halfsize = self.grid.tilesize[1 - int(curdir/2)]/2
			if mod % int(2*halfsize) < halfsize:
				step = 1
			else:
				step = -1
		else:
			step = 0

		return self.direction*3 + 1 + step
