import pygame


class Entity:
    """
    A class representing a movable entity on the map that can switch sprites
    while moving. Movement has to be managed outside the class since it needs
    access to the screen and the map, but this class provides tools to make
    it easy.

    :pos: Position on the map in tile. Should always be a 2-tuple of integers.
    :map_pos: Accurate position on the map in pixels. Should always be a
        2-tuple of integers.
    :direction: The direction this entity points toward.
    :posture: The list of sprites surface for current posture and direction.
    :postures: A dictionary of nested iterable. Each entry should contain an
        iterable of length 4 (for each directions), containing an ordered
        iterable for each sprite making the animation. This makes calling for
        specific sprite easy for every posture and direction, by getting
        person.postures[posture][direction][nth_sprite].
    :sprite_speed: The number of sprites to display for each tile ran through.
    :speed: The speed in pixel per frame of the entity.
    """
    def __init__(self, sprites_files, sprite_size, direction, posture):
        """
        :param sprites_files: an iterable of file names for this entity's
            sprites.
        :param sprite_size: The size in pixel of the sprite as a 2-tuple for
            horizontal and vertical dimensions, respectively.
        :param direction: The initial direction of the entity
        """
        self.pos = self.map_pos = (0, 0)
        self.sprite_size = sprite_size
        self._direction = direction
        self._old_direction = direction
        self.running = True

        self.sprites = []
        for file in sprites_files: # For every sprite file
            # Load image from file
            image = pygame.image.load(file).convert_alpha()
            image_width, image_height = image.get_size()
            # We suppose there is 12 sprites on one line in the file
            for x in range(0, 12):
                rect = (
                    int(image_width / 12) * x, 0, int(image_width / 12),
                    image_height)
                # Rescale the sprite in desired rect box to desired size
                surf = pygame.transform.smoothscale(
                    image.subsurface(rect), sprite_size)
                # Add loaded sprite to sprites list
                self.sprites.append(surf)

        self._posture = []
        self._current_sprite = 0
        # Setup of postures
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
        # Initiates posture
        self.posture = self.def_posture = posture

    def get_sprite_offset(self):
        """
        :return: The offset of sprites' index for current posture due to the
            tile position of the entity on the map.
        """
        return self.pos[int(self._direction < 3)] % int(
            len(self._posture) / self.sprites_speed)

    def next_sprite(self):
        """
        :return: The index of the next sprite to display in the posture.
        """
        self._current_sprite = self._current_sprite + 1 \
            % len(self.posture[self._direction - 1])
        return self.sprites[self._current_sprite]

    @property
    def direction(self):
        if self._direction == 0:
            return self._old_direction
        else:
            return self._direction

    @direction.setter
    def direction(self, direction):
        if 0 != self._direction:
            self._old_direction = self._direction
        self._direction = direction

    @property
    def posture(self):
        """
        Posture property getter.
        """
        return self._posture[self.direction - 1]

    @posture.setter
    def posture(self, posture):
        """
        Posture property setter.
        """
        self._posture = self.postures[posture]
        self._current_sprite = self._posture[self.direction - 1][0]

    def set_pos(self, grid, position, posture=None):
        """
        Force the entity to move to given position instantly. Posture is
        reset to default (or given one).

        :param grid: The grid the entity belongs to.
        :param position: The new entity's position.
        :param posture: The posture the entity should adopt (None for default
            one).
        """
        x_ts, y_ts = grid.tilesize
        x, y = position
        self.map_pos = int(x_ts*x), int(y_ts*y)
        self.pos = int(x), int(y)
        self.posture = posture if posture is not None else self.def_posture

    def update(self, direction, grid):
        """
        Updates the position, direction and posture of the player, given its
        position in the map.
        :return: The new coordinates of the player on the map, in screen pixels.
        """
        # Offset from the position fitting precisely into a tile
        grid_offset_x, grid_offset_y = grid.get_mod()

        # If player is fitting onto a tile
        if grid_offset_y + grid_offset_x == 0:
            # Update its position to this tile
            self.pos = int(self.map_pos[0] / grid.tilesize[0]), \
                              int(self.map_pos[1] / grid.tilesize[1])
            # Update its direction
            self.direction = direction
        # If entity is between two tiles, ignore keyboard entries and
        # continue straight forward to next tile, direction don't change

        # Move if needed
        self.move(grid.level.map)

        return self.map_pos[0], self.map_pos[1]

    def move(self, terrain):
        """
        Check for collisions in front of the entity and move if possible. If no
        direction is selected (_direction = 0), don't move.

        :param terrain: The map as an iterable of line containing the
        terrain, terrain[y][x].
        :return: True if player moved forward, False otherwise.
        """
        x, y = self.pos
        s_x, s_y = self.map_pos
        speed_bonus = 1 + int(self.running) # True -> 1, False -> 0
        # Still posture by default
        self.posture = 'still'
        if self._direction == 1:
            y -= 1
            s_y -= self.speed * speed_bonus
        elif self._direction == 2:
            y += 1
            s_y += self.speed * speed_bonus
        elif self._direction == 3:
            x -= 1
            s_x -= self.speed * speed_bonus
        elif self._direction == 4:
            x += 1
            s_x += self.speed * speed_bonus
        else: # _direction == 0 (or invalid case, but shouldn't happen)
            return False
        can_move = terrain[y][x] not in ('o',)
        if can_move:
            # Update its posture to a moving one
            if self.running:
                self.posture = 'running'
            else:
                self.posture = 'walking'
            # And move (well, validate movement calculated few lines up)
            self.map_pos = s_x, s_y
        return can_move


class Player(Entity):
    """
    Same as a Entity object, except that a Player entity is the "reference"
    for drawing, as it is the only fixed point of the map as drawn on the
    screen. It has thus one more attribute for that. Since the Player objects
    is the reference for all positions, it needs to be updated first on every
    frames.

    :screen_pos: The position on the screen in pixel. This allows us to know
        the position of the map depending on the entity's position.
    """
    def __init__(self, screen, grid, sprites_files, sprite_size, direction,
                 posture):
        """
        Initiates the player object into the map.
        """
        Entity.__init__(self, sprites_files, sprite_size, direction, posture)
        # Put the player in the center of the screen, then computes to which
        # coordinates it correspond in the map.
        # The player position is adjusted so that it is precisely fitting in
        # a tile, even if he is no longer precisely in the center of the screen
        size = screen.get_size()
        x = (size[0] / 2 - grid.screen_pos[0]) // grid.tilesize[0]
        y = (size[1] / 2 - grid.screen_pos[1]) // grid.tilesize[1]
        self.pos = int(x), int(y)
        # Then computes its coordinates pixel accurately on the map for
        # reference
        x = x * grid.tilesize[0]
        y = y * grid.tilesize[1]
        self.map_pos = int(x), int(y)
        # Then pixel coordinates on the screen
        x += grid.screen_pos[0]
        y += grid.screen_pos[1]
        self.screen_pos = int(x), int(y)

