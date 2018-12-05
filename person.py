import pygame


class Person:
    def __init__(self, sprites_files, sprite_size, direction):
        self.pos = self.screen_pos = (0, 0)
        self.sprite_size = sprite_size
        self._direction = direction
        self.speed = 0
        self.running = True

        self.sprites = []
        for file in sprites_files:
            image = pygame.image.load(file).convert_alpha()
            image_width, image_height = image.get_size()
            for x in range(0, 12):
                rect = (
                    int(image_width / 12) * x, 0, int(image_width / 12),
                    image_height)
                surf = pygame.transform.smoothscale(
                    image.subsurface(rect), sprite_size)
                self.sprites.append(surf)

        self.postures = {}
        self.sprites_speed = 0
        self._posture = []
        self._current_sprite = 0

    def get_sprite_offset(self):
        return self.pos[int(self._direction < 2)] % int(
            len(self._posture) / self.sprites_speed)

    def next_sprite(self):
        self._current_sprite = self._current_sprite + 1 \
                               % len(self.posture[self.direction])
        return self.sprites[self._current_sprite]

    @property
    def direction(self):
        return self._direction + 1

    @direction.setter
    def direction(self, direction):
        if direction <= 0:
            return
        self._direction = direction - 1

    @property
    def posture(self):
        return self._posture[self._direction]

    @posture.setter
    def posture(self, posture):
        self._posture = self.postures[posture]
        self._current_sprite = self._posture[self._direction][0]


class Player(Person):
    def __init__(self, sprites_files, sprite_size, direction):
        Person.__init__(self, sprites_files, sprite_size, direction)

        self.postures = {
            'still': [
                [1],
                [4],
                [7],
                [10],
                ],
            'walking': [
                [0, 1, 2, 1],
                [3, 4, 5, 4],
                [6, 7, 8, 7],
                [9, 10, 11, 10],
                ],
            'running': [
                [12, 13, 14, 13],
                [15, 16, 17, 16],
                [18, 19, 20, 19],
                [21, 22, 23, 22]
                ],
            }
        self.sprites_speed = 2
        self.speed = 2
