from Level import Level

class Grid:
	def __init__(self,levelmap,screen,grid_dim,view_coord):
		self.screen     = screen                                 # pygame display
		self.size       = grid_dim                               # tuple, grid dimensions (horizontal tiles, vertical tiles)
		self.view_coord = view_coord                           # View coordinates (offset from (0,0), in pixels)
		self.tilesize   = (screen.get_rect().width/grid_dim[0],  # tuple, size of tiles in pixel (horizontal, vertical)
				         screen.get_rect().height/grid_dim[1]) 
		self.setLevel(levelmap)                                # set levelmap (filename)

	def setLevel(self,levelmap):
		self.level = Level(levelmap)
		self.background = self.level.render(self.screen,self.size)
	
	def getMod(self):
		return self.view_coord[0] % (self.tilesize[0]) + self.view_coord[1] % (self.tilesize[1])
