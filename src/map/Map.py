from src.entity.Space import Space
from src.map.Tile import Tile


class Map:
    def __init__(self):
        self.tiles = {}

    def get_tile(self, x=None, y=None):
        tmp = Space(x, y)
        if tmp.x not in self.tiles:
            self.tiles[tmp.x] = {}
        if tmp.y not in self.tiles[tmp.x]:
            self.tiles[tmp.x][tmp.y] = Tile(tmp.x, tmp.y)
        return self.tiles[tmp.x][tmp.y]
