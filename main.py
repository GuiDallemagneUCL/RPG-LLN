import pygame
import pygame.locals
import numpy
from Level import Level
from Grid import Grid
from Person import Person, Player
import time
import sys
import asyncio


if sys.version_info < (3, 7):
    raise RuntimeError('Python3.7+ needed to run.')

# TODO perf bench compared to synchronously managed tasks

grid_width = 30
grid_height = 20
clock = pygame.time.Clock()

screen = pygame.display.set_mode((960, 640))
grid = Grid("level.map", screen, (grid_width, grid_height), (0, 0))
player = Player("res/trainer_running.png", (10, 10), grid, 1)

current_direction = [0, 0, 0, 0]
old_current_direction = current_direction.copy()

# load button and getting his collide zone
bouton = pygame.image.load("images/sound_icon.png")
bouton_rect = bouton.get_rect()

sound_played = False
running = False

key_direction_mapping = {pygame.locals.K_UP: 0,
                         pygame.locals.K_DOWN: 1,
                         pygame.locals.K_LEFT: 2,
                         pygame.locals.K_RIGHT: 3}
# Useless  to go < 1e-4, this controls game tick speed
# (roughly, not the same as fps)
wait_delay = 1e-4

monitoring_data = {'event/s': 0,
                   'handled-event/s': 0,
                   'click/s': 0,
                   'frame/s': 0,
                   'handle_mouse-call/s': 0,
                   'handle_events-call/s': 0,
                   'handle_grid-call/s': 0,
                   'monitoring-call/s': 0,
                   '_events': 0,
                   '_handled-events': 0,
                   '_clicks': 0,
                   '_frames': 0,
                   '_handle_mouse-calls': 0,
                   '_handle_events-calls': 0,
                   '_handle_grid-calls': 0,
                   '_monitoring-calls': 0,
                   }


async def monitoring():
    while running:
        ellapsed = time.time()
        await asyncio.sleep(1)
        ellapsed = time.time() - ellapsed

        monitoring_data['event/s'] = monitoring_data['_events']/ellapsed
        monitoring_data['handled-event/s'] = monitoring_data['_handled-events']/ellapsed
        monitoring_data['click/s'] = monitoring_data['_clicks']/ellapsed
        monitoring_data['frame/s'] = monitoring_data['_frames']/ellapsed
        monitoring_data['handle_mouse-call/s'] = monitoring_data['_handle_mouse-calls']/ellapsed
        monitoring_data['handle_events-call/s'] = monitoring_data['_handle_events-calls']/ellapsed
        monitoring_data['handle_grid-call/s'] = monitoring_data['_handle_grid-calls']/ellapsed
        monitoring_data['monitoring-call/s'] = monitoring_data['_monitoring-calls']/ellapsed

        print('\nMONITORING:')
        for k, v in monitoring_data.items():
            if not k.startswith('_'):
                print('[] ' + k + ': ' + str(v))

        monitoring_data['_events'] = \
            monitoring_data['_handled-events'] = \
            monitoring_data['_clicks'] = \
            monitoring_data['_frames'] = \
            monitoring_data['_handle_mouse-calls'] = \
            monitoring_data['_handle_events-calls'] = \
            monitoring_data['_handle_grid-calls'] = 0
        monitoring_data['_monitoring-calls'] = 1


async def handle_mouse():
    global bouton, bouton_rect, sound_played, running, monitoring_data
    while running:
        ## Si le focus est sur la fenêtre.
        if pygame.mouse.get_focused():
            ## Trouve position de la souris
            x, y = pygame.mouse.get_pos()
            ## S'il y a collision:
            collide = bouton_rect.collidepoint(x, y)

            ## Détecte les clique de souris.
            pressed = pygame.mouse.get_pressed()
            if pressed[0] and collide:  # 0=gauche, 1=milieu, 2=droite
                if sound_played:
                    bouton = pygame.image.load("images/no_sound_icon.png")
                    pygame.mixer.music.stop()
                    sound_played = False
                else:
                    bouton = pygame.image.load("images/sound_icon.png")
                    pygame.mixer.music.play(-1, 0.0)
                    sound_played = True
                monitoring_data['_clicks'] += 1
                await asyncio.sleep(0.1)
        monitoring_data['_handle_mouse-calls'] += 1
        await asyncio.sleep(wait_delay)


async def handle_grid():
    global current_direction, old_current_direction, bouton, running, screen,\
        player, clock, grid, grid_width, grid_height, monitoring_data
    while running:
        screen.blit(grid.background, grid.view_coord)
        player.blit(screen, player.movement(old_current_direction))
        bouton = pygame.transform.scale(bouton, (32, 32))
        screen.blit(bouton, (0, 0))
        pygame.display.flip()

        #print(grid.view_coord)
        grid_offset_x = grid.view_coord[0] % (
                    screen.get_rect().width / grid_width)
        grid_offset_y = grid.view_coord[1] % (
                    screen.get_rect().height / grid_height)

        if grid_offset_y + grid_offset_x == 0:
            grid.view_coord = updateViewCoordinates(grid.view_coord,
                                                    current_direction, player)
            old_current_direction = current_direction.copy()
        # player.updatePos()
        else:
            grid.view_coord = updateViewCoordinates(grid.view_coord,
                                                    old_current_direction,
                                                    player)
            monitoring_data['_frames'] += 1
            await asyncio.sleep(0.02) # This controls fps (roughly)
        monitoring_data['_handle_grid-calls'] += 1
        await asyncio.sleep(wait_delay)


async def handle_events():
    global current_direction, old_current_direction, bouton, running, screen,\
        player, clock, grid, grid_width, grid_height, monitoring_data
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                monitoring_data['_handled-events'] += 1
            if event.type == pygame.locals.KEYDOWN \
                    and event.key in key_direction_mapping:
                current_direction[key_direction_mapping[event.key]] = max(
                        current_direction) + 1
                monitoring_data['_handled-events'] += 1
            elif event.type == pygame.locals.KEYUP \
                    and event.key in key_direction_mapping:
                current_direction[key_direction_mapping[event.key]] = 0
                monitoring_data['_handled-events'] += 1
            monitoring_data['_events'] += 1

        monitoring_data['_handle_events-calls'] += 1
        await asyncio.sleep(wait_delay)


async def main():
    global grid_width, grid_height, clock, screen, grid, player, \
        current_direction, old_current_direction, bouton, bouton_rect, \
        sound_played, running

    pygame.init()
    pygame.display.set_caption("RPG - Louvain-la-Neuve")

    screen.blit(grid.background, grid.view_coord)
    player.blit(screen, 1)
    pygame.display.flip()

    # sound played
    sound_played = True

    # load music
    pygame.mixer.init()
    pygame.mixer.music.load("sound/lln_sound.wav")
    pygame.mixer.music.play(-1, 0.0)
    running = True

    await asyncio.gather(handle_events(), handle_mouse(), handle_grid(), monitoring())


def updateDirection(event, current_direction):
    if event.type == pygame.locals.KEYDOWN:
        if event.key == pygame.locals.K_UP:
            current_direction[0] = max(current_direction) + 1
        elif event.key == pygame.locals.K_DOWN:
            current_direction[1] = max(current_direction) + 1
        elif event.key == pygame.locals.K_LEFT:
            current_direction[2] = max(current_direction) + 1
        elif event.key == pygame.locals.K_RIGHT:
            current_direction[3] = max(current_direction) + 1
    elif event.type == pygame.locals.KEYUP:
        if event.key == pygame.locals.K_UP:
            current_direction[0] = 0
        elif event.key == pygame.locals.K_DOWN:
            current_direction[1] = 0
        elif event.key == pygame.locals.K_LEFT:
            current_direction[2] = 0
        elif event.key == pygame.locals.K_RIGHT:
            current_direction[3] = 0


def updateViewCoordinates(view_coord, current_direction, player):
    mindir = 1e6
    curdir = 0
    for i in range(0, len(current_direction)):
        if current_direction[i] != 0 and current_direction[i] < mindir:
            mindir = current_direction[i]
            curdir = i + 1

    if curdir == 1:
        view_coord = (view_coord[0], view_coord[1] + player.speed)
    elif curdir == 2:
        view_coord = (view_coord[0], view_coord[1] - player.speed)
    elif curdir == 3:
        view_coord = (view_coord[0] + player.speed, view_coord[1])
    elif curdir == 4:
        view_coord = (view_coord[0] - player.speed, view_coord[1])
    return view_coord


if __name__ == "__main__":
    asyncio.run(main())
