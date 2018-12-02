import pygame
import pygame.locals
from Grid import Grid
from Person import Player
import time
import sys
import asyncio


if sys.version_info < (3, 7):
    raise RuntimeError('Python3.7+ needed to run.')

# TODO perf bench compared to synchronously managed tasks


class LlnRpg:

    key_direction_mapping = {
        pygame.locals.K_UP: 0,
        pygame.locals.K_DOWN: 1,
        pygame.locals.K_LEFT: 2,
        pygame.locals.K_RIGHT: 3
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

    def __init__(self):
        self.grid_width = 30
        self.grid_height = 20

        self.screen = pygame.display.set_mode((960, 640))
        self.grid = Grid("level.map", self.screen,
                         (self.grid_width, self.grid_height), (0, 0))
        self.player = Player("res/trainer_running.png", (10, 10), self.grid, 1)

        self.current_direction = [0, 0, 0, 0]
        self.old_current_direction = self.current_direction.copy()

        # load button and getting his collide zone
        self.bouton = pygame.image.load("images/sound_icon.png")
        self.bouton_rect = self.bouton.get_rect()

        self.sound_played = False
        self.running = False
        # Useless  to go < 1e-4, this controls game tick speed
        # (roughly, not the same as fps)
        # Think of it as "how fast will the game compute things"
        self.wait_delay = 1e-4

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
                await asyncio.sleep(self.wait_delay)
            x, y = pygame.mouse.get_pos()
            # 0=gauche, 1=milieu, 2=droite
            if self.bouton_rect.collidepoint(x, y):
                if self.sound_played:
                    self.bouton = pygame.image.load("images/no_sound_icon.png")
                    pygame.mixer.music.stop()
                    self.sound_played = False
                else:
                    self.bouton = pygame.image.load("images/sound_icon.png")
                    pygame.mixer.music.play(-1, 0.0)
                    self.sound_played = True
                self.monitoring_data['handled-clicks'] += 1
                # wait until mouse unpressed
                # TODO solve bug happening when leaving focus but still pressed
                while self.running and (pygame.mouse.get_focused()
                                        and pygame.mouse.get_pressed()[0]):
                    await asyncio.sleep(self.wait_delay)
            self.monitoring_data['clicks'] += 1
            await asyncio.sleep(self.wait_delay) # avoiding too fast spam click
        print('Closed mouse handler')

    async def handle_graphics(self):
        while self.running:
            self.screen.blit(self.grid.background, self.grid.view_coord)
            self.player.blit(self.screen, self.player.movement(
                self.old_current_direction))
            self.bouton = pygame.transform.scale(self.bouton, (32, 32))
            self.screen.blit(self.bouton, (0, 0))
            pygame.display.flip()

            grid_offset_x = self.grid.view_coord[0] % (
                    self.screen.get_rect().width / self.grid_width)
            grid_offset_y = self.grid.view_coord[1] % (
                    self.screen.get_rect().height / self.grid_height)

            if grid_offset_y + grid_offset_x == 0:
                self.update_view_coordinates(self.current_direction)
                self.old_current_direction = self.current_direction.copy()
            # player.updatePos()
            else:
                self.update_view_coordinates(self.old_current_direction)
            self.monitoring_data['frames'] += 1
            await asyncio.sleep(0.02) # This controls fps (roughly)
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
            await asyncio.sleep(self.wait_delay)
        print('Closed events handler')

    async def main(self):
        pygame.init()
        pygame.display.set_caption("RPG - Louvain-la-Neuve")

        self.screen.blit(self.grid.background, self.grid.view_coord)
        self.player.blit(self.screen, 1)
        pygame.display.flip()

        # sound played
        self.sound_played = True

        # load music
        pygame.mixer.init()
        pygame.mixer.music.load("sound/lln_sound.wav")
        pygame.mixer.music.play(-1, 0.0)
        self.running = True

        await asyncio.gather(self.handle_events(), self.handle_mouse(),
                             self.handle_graphics(), self.monitoring())
        print('Exit main')

    def update_view_coordinates(self, current_direction):
        mindir = max(current_direction)+1
        curdir = 0
        for i in range(0, len(current_direction)):
            if 0 < current_direction[i] < mindir:
                mindir = current_direction[i]
                curdir = i + 1

        if curdir == 1:
            self.grid.view_coord = (self.grid.view_coord[0],
                                    self.grid.view_coord[1] + self.player.speed)
        elif curdir == 2:
            self.grid.view_coord = (self.grid.view_coord[0],
                                    self.grid.view_coord[1] - self.player.speed)
        elif curdir == 3:
            self.grid.view_coord = (self.grid.view_coord[0] + self.player.speed,
                                    self.grid.view_coord[1])
        elif curdir == 4:
            self.grid.view_coord = (self.grid.view_coord[0] - self.player.speed,
                                    self.grid.view_coord[1])


if __name__ == "__main__":
    game = LlnRpg()
    asyncio.run(game.main())
