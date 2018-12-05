import numpy
import pygame
import pygame.locals
from grid import Grid
from person import Player
import time
import sys
import asyncio

if sys.version_info < (3, 7):
    raise RuntimeError('Python3.7+ needed to run.')


# TODO perf bench compared to synchronously managed tasks

def get_direction(direction):
    mindir = max(direction) + 1
    curdir = 0
    for i in range(0, len(direction)):
        if 0 < direction[i] < mindir:
            mindir = direction[i]
            curdir = i + 1
    return curdir


def get_animated_sprite(person, grid, coord):
    i = int(person.direction < 3)
    coord, tilesize = coord[i], grid.tilesize[i]
    sprite = int(coord*person.sprites_speed/tilesize) % len(person.posture)
    return person.posture[sprite]


class LlnRpg:
    key_direction_mapping = {
        pygame.locals.K_UP: 0,
        pygame.locals.K_DOWN: 1,
        pygame.locals.K_LEFT: 2,
        pygame.locals.K_RIGHT: 3,
        }

    monitoring_data = {
        'events': 0.0,
        'handled-events': 0.0,
        'clicks': 0.0,
        'handled-clicks': 0.0,
        'frames': 0.0,
        'handle_events-loops': 0.0,
        'monitoring-interval': 0.0,
        }

    def __init__(self, **kwargs):
        self.grid_width = kwargs.get('grid_width', 30)
        self.grid_height = kwargs.get('grid_height', 20)

        self.screen = pygame.display.set_mode(kwargs.get('screen_mode',
                                                         (960, 640)))
        self.grid = Grid(kwargs.get('map_file', "level.map"),
                         self.screen,
                         (self.grid_width, self.grid_height),
                         kwargs.get('map_pos', (32*4, 32*2)))
        self.player = kwargs.get('player', Player(['res/trainer_walking.png',
                                                   'res/trainer_running.png'],
                                                  self.grid.tilesize, 1))

        self.current_direction = kwargs.get('_direction', [0, 0, 0, 0])
        self.old_current_direction = self.current_direction.copy()

        # load button and getting his collide zone
        self.bouton = pygame.image.load("images/sound_icon.png")
        self.bouton = pygame.transform.scale(self.bouton, (32, 32))
        self.bouton_rect = self.bouton.get_rect()

        self.sound_played = not kwargs.get('play_sound', False)
        self.running = False
        # Useless  to go < 1e-4, this controls game tick speed
        # (roughly, not the same as fps)
        # Think of it as "how fast will the game compute things"
        self.base_delay = kwargs.get('base_delay', 1e-3)

    async def monitoring(self):
        while self.running:
            elapsed = time.time()
            await asyncio.sleep(1)
            elapsed = time.time() - elapsed

            self.monitoring_data['monitoring-interval'] = elapsed
            print('MONITORING:')
            for k, v in self.monitoring_data.items():
                print('[] ' + k + ': ' + str(v))
            print('')

            for k, v in self.monitoring_data.items():
                self.monitoring_data[k] = 0.0
        print('Closed monitoring')

    async def handle_mouse(self):
        while self.running:
            ## Détecte les clique de souris.
            while self.running and not (pygame.mouse.get_focused()
                                        and pygame.mouse.get_pressed()[0]):
                await asyncio.sleep(self.base_delay)
            x, y = pygame.mouse.get_pos()
            # 0=gauche, 1=milieu, 2=droite
            if self.bouton_rect.collidepoint(x, y):
                self.monitoring_data['handled-clicks'] += 1
                self.toggle_sound()
                # wait until mouse unpressed
                # TODO solve bug happening when leaving focus but still pressed
                while self.running and (pygame.mouse.get_focused()
                                        and pygame.mouse.get_pressed()[0]):
                    await asyncio.sleep(self.base_delay)
            self.monitoring_data['clicks'] += 1
            await asyncio.sleep(self.base_delay)  # avoiding too fast spam click
        print('Closed mouse handler')

    async def handle_graphics(self):
        size = self.screen.get_size()
        x = (size[0]/2 - self.grid.screen_pos[0]) // self.grid.tilesize[0]
        y = (size[1]/2 - self.grid.screen_pos[1]) // self.grid.tilesize[1]
        self.player.pos = int(x), int(y)
        print(x, y)
        x = x * self.grid.tilesize[0] + self.grid.screen_pos[0]
        y = y * self.grid.tilesize[1] + self.grid.screen_pos[1]
        self.player.screen_pos = int(x), int(y)
        print(x, y)

        self.player.posture = 'still'
        self.player.direction = 1
        while self.running:
            direction = get_direction(self.current_direction)

            grid_offset_x, grid_offset_y = self.grid.get_mod()
            pos_x = self.player.screen_pos[0] - self.grid.view_coord[0]
            pos_y = self.player.screen_pos[1] - self.grid.view_coord[1]

            if grid_offset_y + grid_offset_x == 0:
                self.player.pos = int(pos_x / self.grid.tilesize[0]), \
                    int(pos_y / self.grid.tilesize[1])
                self.player.direction = direction

                if direction != 0 and self.check_collision(direction):
                    self.update_view_coordinates(direction)
                else:
                    self.player.posture = 'still'
                self.old_current_direction = self.current_direction.copy()
            else:
                posture = 'running' if self.player.running else 'walking'

                if self.check_collision():
                    self.update_view_coordinates(get_direction(
                        self.old_current_direction))
                else:
                    posture = 'still'
                self.player.posture = posture

            self.screen.blit(self.grid.background, self.grid.view_coord)
            self.screen.blit(self.bouton, (0, 0))
            self.screen.blit(
                self.player.sprites[get_animated_sprite(
                    self.player, self.grid, (pos_x, pos_y))],
                (int(self.player.screen_pos[0]),
                 int(self.player.screen_pos[1])))

            pygame.display.flip()
            self.monitoring_data['frames'] += 1
            await asyncio.sleep(0.015)  # This controls fps (roughly)
        print('Closed graphics handler')

    async def handle_events(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.monitoring_data['handled-events'] += 1

                if event.type == pygame.locals.KEYDOWN \
                        and event.key in self.key_direction_mapping:
                    self.current_direction[self.key_direction_mapping[
                        event.key]] = max(self.current_direction) + 1
                    self.monitoring_data['handled-events'] += 1

                elif event.type == pygame.locals.KEYUP \
                        and event.key in self.key_direction_mapping:
                    self.current_direction[self.key_direction_mapping[
                        event.key]] = 0
                    self.monitoring_data['handled-events'] += 1
                self.monitoring_data['events'] += 1
            self.monitoring_data['handle_events-loops'] += 1
            await asyncio.sleep(self.base_delay)
        print('Closed events handler')

    async def main(self):
        pygame.init()
        pygame.display.set_caption("RPG - Louvain-la-Neuve")

        self.screen.blit(self.grid.background, self.grid.view_coord)
        pygame.display.flip()

        # load music
        pygame.mixer.init()
        pygame.mixer.music.load("sound/lln_sound.wav")
        pygame.mixer.music.play(-1, 0.0)
        self.toggle_sound()
        self.running = True

        await asyncio.gather(self.handle_events(), self.handle_mouse(),
                             self.handle_graphics(), self.monitoring())
        print('Exit main')

    def toggle_sound(self):
        if self.sound_played:
            self.bouton = pygame.image.load("images/no_sound_icon.png")
            self.bouton = pygame.transform.scale(self.bouton, (32, 32))
            pygame.mixer.music.stop()
            self.sound_played = False
        else:
            self.bouton = pygame.image.load("images/sound_icon.png")
            self.bouton = pygame.transform.scale(self.bouton, (32, 32))
            pygame.mixer.music.play(-1, 0.0)
            self.sound_played = True

    def update_view_coordinates(self, direction):
        speed = self.player.speed
        if self.player.running:
            speed *= 2
        if direction == 1:
            self.grid.view_coord = (self.grid.view_coord[0],
                                    self.grid.view_coord[1] + speed)
        elif direction == 2:
            self.grid.view_coord = (self.grid.view_coord[0],
                                    self.grid.view_coord[1] - speed)
        elif direction == 3:
            self.grid.view_coord = (self.grid.view_coord[0] + speed,
                                    self.grid.view_coord[1])
        elif direction == 4:
            self.grid.view_coord = (self.grid.view_coord[0] - speed,
                                    self.grid.view_coord[1])

    def check_collision(self, direction=None):
        if direction is None:
            direction = get_direction(self.old_current_direction)
        x, y = self.player.pos
        if direction == 1:
            y -= 1
        if direction == 2:
            y += 1
        if direction == 3:
            x -= 1
        if direction == 4:
            x += 1
        return self.grid.level.map[y][x] not in ('o',)


if __name__ == "__main__":
    game = LlnRpg()
    asyncio.run(game.main())
