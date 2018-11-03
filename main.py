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

    #load button and getting his collide zone
	bouton = pygame.image.load("images/sound_icon.png")
	bouton_rect = bouton.get_rect()

	#sound played
	sound_played = True

	#load music
	pygame.mixer.init()
	pygame.mixer.music.load("sound/lln_sound.wav")
	pygame.mixer.music.play(-1,0.0)

	while running:
		screen.blit(background,view_coord)
		bouton = pygame.transform.scale(bouton, (32, 32))
		screen.blit(bouton, (0,0))
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
			## Si le focus est sur la fenêtre.
			if pygame.mouse.get_focused():
				## Trouve position de la souris
				x, y = pygame.mouse.get_pos()
				## S'il y a collision:
				collide = bouton_rect.collidepoint(x, y)

				## Détecte les clique de souris.
				pressed = pygame.mouse.get_pressed()
				if pressed[0] and collide: # 0=gauche, 1=milieu, 2=droite
					if sound_played:
						bouton = pygame.image.load("images/no_sound_icon.png")
						pygame.mixer.music.stop()
						sound_played = False
					else:
						bouton = pygame.image.load("images/sound_icon.png")
						pygame.mixer.music.play(-1,0.0)
						sound_played = True

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
