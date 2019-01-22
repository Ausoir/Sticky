from src.entity.Space import Space
from src.map.Terrain import Terrain


class Tile(Space):
    BLOCK = 40
    Terrain.BLOCK = BLOCK
    CHECK_NONE = 0
    CHECK_ANY = 1
    CHECK_TERRAIN = 2

    def __init__(self, x, y):
        super().__init__(x, y)
        self.terrain = None
        self.things = []

    def set_terrain(self, terrain):
        self.terrain = Terrain.make(terrain, self * [Tile.BLOCK, Tile.BLOCK])

    def remove(self, thing):
        if thing in self.things:
            self.things.remove(thing)

    def draw(self, surface):
        if self.terrain:
            self.terrain.draw(surface)

    def draw_objects(self, surface):
        vec = self.get_vec()
        boundary = [vec[0] + Tile.BLOCK / 2, vec[1]]
        for thing in self.things:
            thing.draw(surface, boundary)

    def get_vec(self):
        return [self.x * Tile.BLOCK, self.y * Tile.BLOCK]

    def is_land(self, type):
        land_terrain = self.terrain and self.terrain.type == 1
        land_unit = len(self.things) > 0
        if type == Tile.CHECK_TERRAIN:
            return land_terrain
        return land_terrain or land_unit
