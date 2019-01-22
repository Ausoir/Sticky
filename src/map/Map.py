from src.entity.Space import Space
from src.map.Tile import Tile
from src.tools.Math import Math


class Map:
    def __init__(self, x, y):
        self.tiles = []
        for iy in range(y):
            row = []
            for ix in range(x):
                row.append(Tile(ix, iy))
            self.tiles.append(row)
        for i in self.tiles[10]:
            i.set_terrain('dirt')
        self.tiles[9][8].set_terrain('dirt')
        self.tiles[5][8].set_terrain('dirt')
        self.tiles[5][7].set_terrain('dirt')
        self.tiles[7][9].set_terrain('dirt')

    def draw(self, surface):
        for i1 in self.tiles:
            for i2 in i1:
                i2.draw(surface)

    def draw_objects(self, surface):
        for i1 in self.tiles:
            for i2 in i1:
                i2.draw_objects(surface)

    def get_tile(self, x=None, y=None):
        return self.tiles[y][x]

    def get_tile_from_vec(self, x, y):
        return self.tiles[int(y / Tile.BLOCK)][int(x / Tile.BLOCK)]

    def collide_line(self, vec_from, x, y, flag=Tile.CHECK_TERRAIN):
        target_pos = vec_from + (x, y)
        degree = Space(x, y).get_atan()
        current = ((vec_from * Tile.BLOCK)+(Tile.BLOCK/2, Tile.BLOCK/2)).to_list()
        prev_tile = vec_from
        while prev_tile.x != target_pos.x or prev_tile.y != target_pos.y:
            current = [current[0] - Math.cos(degree)*Tile.BLOCK, current[1] + Math.sin(degree)*Tile.BLOCK]
            tile = self.get_tile_from_vec(current[0], current[1])
            if tile.is_land(flag):
                return prev_tile
            tile.set_terrain('mark')
            prev_tile = tile
        return prev_tile
