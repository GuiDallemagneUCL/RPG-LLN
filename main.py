import pygame
import pygame.locals
import numpy
from Level import Level

class Grid:
	def __init__(self,levelmap,screen,grid_dim):
		self.screen   = screen                                 # pygame display
		self.size     = grid_dim                               # tuple, grid dimensions (horizontal tiles, vertical tiles)
		self.tilesize = (screen.get_rect().width/grid_dim[0],  # tuple, size of tiles in pixel (horizontal, vertical)
				         screen.get_rect().height/grid_dim[1]) 
		self.setLevel(levelmap)                                # set levelmap (filename)

	def setLevel(self,levelmap):
		self.level = Level(levelmap)
		self.background = self.level.render(self.screen,self.size)
 
def main():
	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption("minimal program")
	screen = pygame.display.set_mode((480,320))
	grid_width = 15
	grid_height = 10

	grid = Grid("level.map",screen,(grid_width,grid_height))


	view_coord = tuple(numpy.subtract((0,0),grid.tilesize))
	screen.blit(grid.background,view_coord)
	pygame.display.flip()

	current_direction = [0,0,0,0]

	running = True
	while running:
		screen.blit(grid.background,view_coord)
		pygame.display.flip()
		clock.tick(60)
		print(current_direction)

		grid_offset_x = view_coord[0] % (screen.get_rect().width/grid_width)
		grid_offset_y = view_coord[1] % (screen.get_rect().height/grid_height)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			updateDirection(event,current_direction)

		if grid_offset_y + grid_offset_x == 0:
			view_coord = updateViewCoordinates(view_coord,current_direction,screen,grid_height,grid_width)
			old_current_direction = current_direction.copy()
		else:
			view_coord = updateViewCoordinates(view_coord,old_current_direction,screen,grid_height,grid_width)
			


def updateDirection(event,current_direction):
	if event.type == pygame.locals.KEYDOWN:
		if keyIsDirection(event.key):
			if event.key == pygame.locals.K_UP:
				current_direction[0] = max(current_direction)+1
			elif event.key == pygame.locals.K_DOWN:
				current_direction[1] = max(current_direction)+1
			elif event.key == pygame.locals.K_LEFT:
				current_direction[2] = max(current_direction)+1
			elif event.key == pygame.locals.K_RIGHT:
				current_direction[3] = max(current_direction)+1
	elif event.type == pygame.locals.KEYUP:
		if keyIsDirection(event.key):
			if event.key == pygame.locals.K_UP:
				current_direction[0] = 0
			elif event.key == pygame.locals.K_DOWN:
				current_direction[1] = 0
			elif event.key == pygame.locals.K_LEFT:
				current_direction[2] = 0
			elif event.key == pygame.locals.K_RIGHT:
				current_direction[3] = 0

def keyIsDirection(key):
	if key == pygame.locals.K_DOWN or key == pygame.locals.K_UP or key == pygame.locals.K_LEFT or key == pygame.locals.K_RIGHT:
		return True
	return False

def updateViewCoordinates(view_coord,current_direction,screen,grid_height,grid_width):
	mindir = 1e6
	curdir = 0
	for i in range(0,len(current_direction)):
		if current_direction[i] != 0 and current_direction[i] < mindir:
			mindir = current_direction[i]
			curdir = i+1

	if curdir == 1:
		#view_coord = (view_coord[0],view_coord[1] + screen.get_rect().height / grid_height)
		view_coord = (view_coord[0],view_coord[1] + 2)
	elif curdir == 2:
		view_coord = (view_coord[0],view_coord[1] - 2)
	elif curdir == 3:
		view_coord = (view_coord[0] + 2, view_coord[1])
	elif curdir == 4:
		view_coord = (view_coord[0] - 2, view_coord[1])
	return view_coord





if __name__=="__main__":
    main()
