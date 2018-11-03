# import the pygame module, so you can use it
import pygame
import pygame.locals
from Level import Level
 


# define a main function
def main():
	pygame.init()
	clock = pygame.time.Clock()
	pygame.display.set_caption("minimal program")
	screen = pygame.display.set_mode((480,320))
	grid_width = 30
	grid_height = 20
	running = True

	level = Level("level.map")
	background = level.render(screen,grid_width,grid_height)
	view_coord = (-screen.get_rect().height/grid_height,-screen.get_rect().width/grid_width)
	screen.blit(background,view_coord)
	pygame.display.flip()

	current_direction = [0,0,0,0]
	while running:
		screen.blit(background,view_coord)
		pygame.display.flip()
		clock.tick(12)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
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




		view_coord = updateViewCoordinates(view_coord,current_direction,screen,grid_height,grid_width)



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
		view_coord = (view_coord[0],view_coord[1] + screen.get_rect().height / grid_height)
	elif curdir == 2:
		view_coord = (view_coord[0],view_coord[1] - screen.get_rect().height / grid_height)
	elif curdir == 3:
		view_coord = (view_coord[0] + screen.get_rect().width / grid_width, view_coord[1])
	elif curdir == 4:
		view_coord = (view_coord[0] - screen.get_rect().width / grid_width, view_coord[1])
	return view_coord





if __name__=="__main__":
    main()
