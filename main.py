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
	grid_width = 15
	grid_height = 10
	running = True

	level = Level("level.map")
	background = level.render(screen,grid_width,grid_height)
	view_coord = (-screen.get_rect().height/grid_height,-screen.get_rect().width/grid_width)
	screen.blit(background,view_coord)
	pygame.display.flip()

	while running:
		screen.blit(background,view_coord)
		pygame.display.flip()
		clock.tick(15)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.locals.KEYDOWN:
				if event.key == pygame.locals.K_DOWN:
					view_coord = (view_coord[0],view_coord[1] - screen.get_rect().height / grid_height)
				elif event.key == pygame.locals.K_UP:
					view_coord = (view_coord[0],view_coord[1] + screen.get_rect().height / grid_height)
				elif event.key == pygame.locals.K_LEFT:
					view_coord = (view_coord[0] + screen.get_rect().width / grid_width, view_coord[1])
				elif event.key == pygame.locals.K_RIGHT:
					view_coord = (view_coord[0] - screen.get_rect().width / grid_width, view_coord[1])

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
