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
        self.map_pos = int(x_ts * x), int(y_ts * y)
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

    This class is meant for subclassing.

    :direction: The direction of the entity, 1: UP, 2: DOWN, 3: LEFT, 4: RIGHT.
    :posture: The list of sprites surface for current posture and direction.
    :postures: A dictionary of nested iterable. Each entry should contain an
        iterable of length 4 (for each directions), containing an ordered
        iterable for each sprite making the animation. This makes calling for
        specific sprite easy for every posture and direction, by getting
        person.postures[posture][direction][nth_sprite].
    :speed: The speed in pixel per frame of the entity.
    :can_move: Flag telling if the entity can move or not.
    """

    def __init__(self, direction, posture, speed, sprite_size=(32, 32),
                 sprite_speed=1, current_sprite=0, pos=(0, 0), map_pos=(0, 0),
                 sprites=None):
        Entity.__init__(self, sprite_size, sprite_speed, current_sprite, pos,
                        map_pos, sprites)
        self._direction = direction
        self._old_direction = direction
        self._can_move = False

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
            }
        self.speed = speed
        # Initiates posture
        self.posture = self.def_posture = posture

    @property
    def can_move(self):
        """
        Can_move property getter. (No setter available)
        """
        return self._can_move

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

    def get_speed(self):
        """
        :return: The relevant speed for current situation.
        """
        return self.speed

    def update_posture(self):
        """
        Updates the posture to the relevant one for current situation.
        """
        pass

    def update(self, direction, grid, full=True):
        """
        Updates the entity's direction position and sprite. This function
        uses current entity's and grid state to animate the entity while moving.

        :param direction: The direction the entity may point to.
        :param grid: The grid this entity belongs to.
        :param full: True (by default) if the entity can update its
            motion-related variables (speed, posture, direction, etc.) and
            move, False if it should just move. Useful when the entity is
            stuck in a position, or jumping.
        """
        # Offset from the position fitting precisely into a tile
        if self.direction > 2:
            offset = self.map_pos[0] % grid.tilesize[0]
        else:
            offset = self.map_pos[1] % grid.tilesize[1]

        # If player is fitting onto a tile and full update True
        if offset == 0 and full:
            # Update its position only in current moving direction, again to
            # allow correction of bad coordinates.
            # + 0.9 to avoid miscalculations due to inexact
            if self.direction > 2:
                self.pos = int(self.map_pos[0] / grid.tilesize[0]), self.pos[1]
            else:
                self.pos = self.pos[0], int(self.map_pos[1] / grid.tilesize[1])
            # Update its direction and speed
            # Speed is updated only when on a tile to avoid bugs.
            # If player can't get precisely on a tile (i.e. when its speed
            # value does not divides the tilesize value, speed % size !=0),
            # it may go through several tiles or even never stop moving this
            # direction
            self.direction = direction
            self.speed = self.get_speed()
        # If entity is between two tiles, ignore keyboard entries and
        # continue straight forward to next tile, direction don't change

        # Move if needed
        x, y = self.pos
        s_x, s_y = self.map_pos
        can_move = True
        if self._direction == 1:
            y -= 1
            s_y -= self.speed
        elif self._direction == 2:
            y += 1
            s_y += self.speed
        elif self._direction == 3:
            x -= 1
            s_x -= self.speed
        elif self._direction == 4:
            x += 1
            s_x += self.speed
        else:  # _direction == 0 (or invalid case, but shouldn't happen)
            can_move = False
        can_move = can_move and grid.level.map[y][x] not in ('o',)
        self._can_move = can_move
        # Update posture, now that we now if we move
        if full:
            self.update_posture()
        if can_move:  # If direction != 0 and no obstacle
            # And move (well, validate movement calculated few lines up)
            self.map_pos = s_x, s_y
        # Eventually update current sprite
        i = int(self.direction < 3)
        coord, tilesize = self.map_pos[i], grid.tilesize[i]
        sprite = int(coord * self.sprites_speed / tilesize) % len(self.posture)
        self.current_sprite = self.posture[sprite]


class Player(Movable, Storage):
    """
    Same as a Movable object, except that a Player entity is the "reference"
    for drawing, as it is the only fixed point of the map as drawn on the
    screen. It has thus one more attribute for that. Since the Player objects
    is the reference for all positions, it needs to be updated first on every
    frames.

    It also has new attributes for its movement particularities, and two new
    postures: running and jumping.

    :screen_pos: The position on the screen in pixel. This allows us to know
        the position of the map depending on the entity's position.
    :running: Flag telling if the player runs or not.
    :jumping: Flag telling if the player is jumping or not.
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
        self._running = self._will_run = False
        self.balance = 0

        # Running posture
        self.postures['running'] = [[12 + 3 * i + j for j in range(3)]
                                    for i in range(4)]

    @property
    def running(self):
        """
        Running property getter
        """
        return self._running

    @running.setter
    def running(self, value):
        """
        Running property setter.
        """
        self._will_run = value

    def update(self, direction, grid, full=True):
        """
        In addition to Movable.update, this function checks if the player is
        on the same tile as a coin, and collects it if it is the case.
        """
        # Update running status if on tile
        if full and (self.map_pos[0] % grid.tilesize[0],
           self.map_pos[1] % grid.tilesize[1]) == (0, 0):
            self._running = self._will_run
        # Calling parent's update function
        Movable.update(self, direction, grid, full)
        # looking for money on the same tile
        for _, entity in grid.entities.items():
            if entity.pos == self.pos and isinstance(entity, Coin):
                entity.collect(self)

    def get_speed(self):
        return 2 * (1 + int(self.running))  # Running: True -> 4, False -> 2

    def update_posture(self):
        if self.running and self.can_move:
            self.posture = 'running'
        elif self.can_move:
            self.posture = 'walking'
        else:
            self.posture = 'still'


class Coin(Entity):
    """
    A collectible coin that will go into player's balance.

    :value: The value of the coin, added to player's balance when collected.
    """

    def __init__(self, sprite_size, value):
        Entity.__init__(self, sprite_size, 1, 0)
        self.value = value
        self._jump_counter = None
        self._frame_counter = 0
        self.sprites_speed = 1

    def update(self, grid):
        """
        Updates the coin on every frame. Animates it when collected,
        then kills itself.

        :param grid: The grid this coin belongs to.
        """
        cnt = self._jump_counter
        if self._frame_counter <= 0:
            self._frame_counter = self.sprites_speed
        else:
            self._frame_counter -= 1
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
