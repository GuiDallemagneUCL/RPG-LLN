from Level import Level


class Grid:
    def __init__(self, levelmap, screen, grid_dim, view_coord):
        self.screen_pos = view_coord
        self.screen = screen  # pygame display
        # tuple, grid dimensions (horizontal tiles, vertical tiles)
        self.size = grid_dim
        # View coordinates (offset from (0,0), in pixels)
        self.view_coord = view_coord
        self.tilesize = int(screen.get_rect().width / grid_dim[0]), \
            int(screen.get_rect().height / grid_dim[1])
        self.level = Level(levelmap)
        self.background = self.level.render(self.screen, self.size)
        self.entities = dict()

    def setLevel(self, levelmap):
        self.level = Level(levelmap)
        self.background = self.level.render(self.screen, self.size)

    def get_mod(self):
        return self.view_coord[0] % self.tilesize[0], \
               self.view_coord[1] % self.tilesize[1]

    def add_entity(self, entity):
        for i in range(len(self.entities) + 1):
            if i not in self.entities:
                self.entities[i] = entity
                return i

    def remove_entity(self, entity):
        for i in self.entities:
            if entity is self.entities[i]:
                del self.entities[i]
                return i
