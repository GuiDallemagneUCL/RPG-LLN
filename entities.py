import pygame
import numpy


class Entity:
    """
    A class representing a basic entity on the map.

    :pos: Position on the map in tile. Should always be a 2-tuple of integers.
    :map_pos: Position on the map in screen pixel. Should always be a 2-tuple of
        integers.
    :sprite_size: A 2-tuple specifying the size (horizontal, vertical) of the
        sprites.
    :sprite_speed: The number of frame to display one sprite before
        displaying next one.
    :current_sprite: The index of the current sprite.
    :sprites: A list of Surface objects that will be used to draw the entity
        on the screen.
    """
    def __init__(self, sprite_size=(32, 32), sprite_speed=1, current_sprite=0,
                 pos=(0, 0), map_pos=(0, 0), sprites=None):
        self.pos = pos
        self.map_pos = map_pos
        self.sprite_size = int(sprite_size[0]), int(sprite_size[1])
        self.sprites_speed = sprite_speed
        self.current_sprite = current_sprite
        self.sprites = [] if sprites is None else sprites
        self.alive = True

    def load_sprites(self, sprites_file, nx, ny):
        """
        Load sprites found in files and add them to this objects' sprites.
        Sprites are supposed to be aligned in a grid, and to have the exact
        same size in pixels. They are rescaled to fit this entity's sprite_size.

        :param sprites_file: An image file containing sprites
        :param nx: number of sprite in the horizontal direction.
        :param ny: number of sprite in the vertical direction.
        """
        # Load image from file
        image = pygame.image.load(sprites_file).convert_alpha()
        image_width, image_height = image.get_size()
        # Size of sprites in file
        size_x = int(image_width / nx)
        size_y = int(image_height / ny)
        for y in range(ny):
            for x in range(nx):
                # top left corner coordinates, x & y dimension
                rect = (size_x * x, size_y * y, size_x, size_y)
                # Rescale the sprite in desired rect box to desired size
                surf = pygame.transform.smoothscale(
                    image.subsurface(rect), self.sprite_size)
                # Add loaded sprite to sprites list
                self.sprites.append(surf)

    def set_pos(self, grid, position):
        """
        Move the entity to given position instantly.

        :param grid: The grid the entity belongs to.
        :param position: The new entity's position.
        """
        x_ts, y_ts = grid.tilesize
        x, y = position
        self.map_pos = int(x_ts*x), int(y_ts*y)
        self.pos = int(x), int(y)

    def blit(self, screen, view_coord):
        """
        Blits the entity on the screen.

        :param screen: The pygame surface object representing the screen to
            blit on.
        :param view_coord: The view's coordinates of the grid.
        """
        screen.blit(self.sprites[self.current_sprite],
                    tuple(numpy.add(self.map_pos, view_coord)))


class Storage(Entity):
    """
    A class for an entity that can store various things.

    :inventory_size: The size of the inventory
    :inventory: An array of any kind of objects, of size inventory_size.
    :item_count: The number of item in the inventory.
    """

    def __init__(self, inventory_size, sprite_size=(32, 32), sprite_speed=1,
                 current_sprite=0, pos=(0, 0), map_pos=(0, 0), sprites=None):
        Entity.__init__(self, sprite_size, sprite_speed, current_sprite, pos,
                        map_pos, sprites)
        self.inventory_size = inventory_size
        self.inventory = {i: None for i in range(inventory_size)}
        self.item_count = 0

    def insert(self, item):
        """
        Inserts an object into the inventory.

        :param item: The object to insert.
        :return: The index of the object if it was inserted, -1 if inventory
        was full.
        """
        if self.item_count >= self.inventory_size:
            return -1
        for i in self.inventory:
            if self.inventory[i] is None:
                self.inventory[i] = item
                self.item_count += 1
                return i

    def remove(self, index):
        """
        Removes an item from the inventory.

        :param index: The index of the object in the inventory
        :return: The object removed.
        """
        item = self.inventory[index]
        self.inventory[index] = None
        self.item_count -= 1
        return item


class Movable(Entity):
    """
    A class representing a moving entity that can switch sprites while moving.
    Movement has to be managed outside the class since it needs access to the
    screen and the map, but this class provides tools to make it easy.

    :direction: The direction of the entity, 1: UP, 2: DOWN, 3: LEFT, 4: RIGHT.
    :posture: The list of sprites surface for current posture and direction.
    :postures: A dictionary of nested iterable. Each entry should contain an
        iterable of length 4 (for each directions), containing an ordered
        iterable for each sprite making the animation. This makes calling for
        specific sprite easy for every posture and direction, by getting
        person.postures[posture][direction][nth_sprite].
    :speed: The speed in pixel per frame of the entity.
    """
    def __init__(self, direction, posture, speed, sprite_size=(32, 32),
                 sprite_speed=1, current_sprite=0, pos=(0, 0), map_pos=(0, 0),
                 sprites=None):
        Entity.__init__(self, sprite_size, sprite_speed, current_sprite, pos,
                        map_pos, sprites)
        self._direction = direction
        self._old_direction = direction

        self._posture = []
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
        self.speed = speed
        # Initiates posture
        self.posture = self.def_posture = posture

    @property
    def direction(self):
        """
        Direction property getter.
        """
        if self._direction == 0:
            return self._old_direction
        else:
            return self._direction

    @direction.setter
    def direction(self, direction):
        """
        Direction property setter.
        """
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
        self.current_sprite = self._posture[self.direction - 1][0]

    def set_pos(self, grid, position, posture=None):
        """
        Force the entity to move to given position instantly. Posture is
        reset to default (or given one).

        :param grid: The grid the entity belongs to.
        :param position: The new entity's position.
        :param posture: The posture the entity should adopt (None for default
            one).
        """
        Entity.set_pos(self, grid, position)
        self.posture = self.def_posture if posture is None else posture

    def get_speed_modifier(self, *args, **kwargs):
        """
        :return: The relevant speed modifier for current situation.
        """
        return 1

    def update_posture(self, *args, **kwargs):
        """
        Updates the posture to the relevant one for current situation.
        """
        pass

    def update(self, direction, grid):
        """
        Updates the entity's direction position and sprite. This function
        uses current entity's and grid state to animate the entity while moving.

        :param direction: The direction the entity may point to.
        :param grid: The grid this entity belongs to.
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
        x, y = self.pos
        s_x, s_y = self.map_pos
        speed_mod = self.get_speed_modifier()
        can_move = True
        if self._direction == 1:
            y -= 1
            s_y -= self.speed * speed_mod
        elif self._direction == 2:
            y += 1
            s_y += self.speed * speed_mod
        elif self._direction == 3:
            x -= 1
            s_x -= self.speed * speed_mod
        elif self._direction == 4:
            x += 1
            s_x += self.speed * speed_mod
        else:  # _direction == 0 (or invalid case, but shouldn't happen)
            can_move = False
        can_move = can_move and grid.level.map[y][x] not in ('o',)
        if can_move: # If direction != 0 and no obstacle
            # Update its posture to a moving one
            self.update_posture()
            # And move (well, validate movement calculated few lines up)
            self.map_pos = s_x, s_y
        else:
            # Still posture by default
            self.posture = 'still'
        # Eventually update current sprite
        i = int(self.direction < 3)
        coord, tilesize = self.map_pos[i], grid.tilesize[i]
        sprite = int(coord * self.sprites_speed / tilesize) % len(self.posture)
        self.current_sprite = self.posture[sprite]


class Player(Movable, Storage):
    """
    Same as a Entity object, except that a Player entity is the "reference"
    for drawing, as it is the only fixed point of the map as drawn on the
    screen. It has thus one more attribute for that. Since the Player objects
    is the reference for all positions, it needs to be updated first on every
    frames.

    :screen_pos: The position on the screen in pixel. This allows us to know
        the position of the map depending on the entity's position.
    :running: Flag telling if the player runs or not.
    :balance: The amount of money owned by the player.
    """

    sprites_files = {
        'male': [
            ('res/trainer_walking.png', 12, 1),
            ('res/trainer_running.png', 12, 1)
            ],
        'female': [
            ('res/trainerg_walking.png', 12, 1),
            ('res/trainerg_running.png', 12, 1),
            ],
        }

    def __init__(self, screen, grid, sex='other', direction=1, posture='still',
                 inventory_size=30):
        Storage.__init__(self, inventory_size)
        Movable.__init__(self, direction, posture, 2, grid.tilesize, 2)
        # Load sprites
        for file, nx, ny in self.sprites_files[sex]:
            self.load_sprites(file, nx, ny)
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

        # Player variables
        self.running = True
        self.balance = 0

    def update(self, direction, grid):
        """
        In addition to Movable.update, this function checks if the player is
        on the same tile as a coin, and collects it if it is the case.
        """
        Movable.update(self, direction, grid)
        for _, entity in grid.entities.items():
            if entity.pos == self.pos and isinstance(entity, Coin):
                entity.collect(self)

    def get_speed_modifier(self):
        return 1 + int(self.running)  # True -> 2, False -> 1

    def update_posture(self):
        # Only called if could move, otherwise posture was set to still
        if self.running:
            self.posture = 'running'
        else:
            self.posture = 'walking'


class Coin(Entity):
    """
    A collectible coin that will go into player's balance.

    :value: The value of the coin, added to player's balance when collected.
    """
    def __init__(self, sprite_size, value):
        Entity.__init__(self, sprite_size, 1, 0)
        self.value = value
        self._jump_counter = None
        self._frame_couter = 0
        self.sprites_speed = 1

    def update(self, grid):
        """
        Updates the coin on every frame. Animates it when collected,
        then kills itself.

        :param grid: The grid this coin belongs to.
        """
        cnt = self._jump_counter
        if self._frame_couter <= 0:
            self._frame_couter = self.sprites_speed
        else:
            self._frame_couter -= 1
            return
        if cnt is not None:
            if cnt < 6:
                self.map_pos = self.map_pos[0], self.map_pos[1] + cnt
                self._jump_counter += 1
            else:
                self._jump_counter = None
                grid.remove_entity(self)

    def collect(self, collector):
        """
        Collect this entity and put it in collector's balance

        :param collector: The collector entity.
        :return: True if collector collected entity, False if failed.
        """
        if not self.alive:
            return False
        try:
            collector.balance += self.value
            self._jump_counter = -6
            self.pos = None
            self.alive = False
            return True
        except AttributeError:
            return False
