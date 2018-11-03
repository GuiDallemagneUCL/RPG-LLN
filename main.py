import pygame
import pygame.locals
import numpy
from Level import Level
from Grid import Grid
from Person import Person, Player

def main():
	pygame.init()
	pygame.display.set_caption("RPG - Louvain-la-Neuve")
	screen      = pygame.display.set_mode((960,640))
	grid_width  = 30
	grid_height = 20
	clock       = pygame.time.Clock()

	grid   = Grid("level.map",screen,(grid_width,grid_height),(0,0))
	player = Player("res/trainer_running.png",(10,10),grid,1)

	screen.blit(grid.background,grid.view_coord)
	player.blit(screen,1)
	pygame.display.flip()

	current_direction     = [0,0,0,0]
	old_current_direction = current_direction.copy()
	grid_offset_x         = grid.view_coord[0] % (screen.get_rect().width/grid_width)
	grid_offset_y         = grid.view_coord[1] % (screen.get_rect().height/grid_height)

    #load button and getting his collide zone
	bouton = pygame.image.load("images/sound_icon.png")
	bouton_rect = bouton.get_rect()

	#sound played
	sound_played = True

	#load music
	pygame.mixer.init()
	pygame.mixer.music.load("sound/lln_sound.wav")
	pygame.mixer.music.play(-1,0.0)
	running = True

	while running:
		screen.blit(grid.background,grid.view_coord)
		player.blit(screen,player.movement(old_current_direction))
		bouton = pygame.transform.scale(bouton, (32, 32))
		screen.blit(bouton, (0,0))
		pygame.display.flip()
		clock.tick(60)

		print(grid.view_coord)
		grid_offset_x = grid.view_coord[0] % (screen.get_rect().width/grid_width)
		grid_offset_y = grid.view_coord[1] % (screen.get_rect().height/grid_height)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			updateDirection(event,current_direction)

		if grid_offset_y + grid_offset_x == 0:
			grid.view_coord = updateViewCoordinates(grid.view_coord,current_direction,player)
			old_current_direction = current_direction.copy()
			#player.updatePos()
		else:
			grid.view_coord = updateViewCoordinates(grid.view_coord,old_current_direction,player)

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

def updateViewCoordinates(view_coord,current_direction,player):
	mindir = 1e6
	curdir = 0
	for i in range(0,len(current_direction)):
		if current_direction[i] != 0 and current_direction[i] < mindir:
			mindir = current_direction[i]
			curdir = i+1

	if curdir == 1:
		view_coord = (view_coord[0],view_coord[1] + player.speed)
	elif curdir == 2:
		view_coord = (view_coord[0],view_coord[1] - player.speed)
	elif curdir == 3:
		view_coord = (view_coord[0] + player.speed, view_coord[1])
	elif curdir == 4:
		view_coord = (view_coord[0] - player.speed, view_coord[1])
	return view_coord

if __name__=="__main__":
    main()
