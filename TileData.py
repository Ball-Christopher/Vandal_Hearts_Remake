
'''
CHRIS

This class holds information on the specific tiles, such as if there
is a unit presently on the tile, if it is passable, and if so
how much it costs to pass.
'''
class TileData:
    def __init__(self, position, mov_cost, Tile, Cell):
        self.position = position
        self.mov_cost = mov_cost
        self.Tile = Tile
        self.Cell = Cell
        self.hasUnit = False
        self.unit = None
        pass

    def AddUnit(self,Unit):
        self.hasUnit = True
        self.unit = Unit