from src.entity.Space import Space
from src.map.Terrain import Terrain
from src.tools.List import List


class Tile(Space):
    BLOCK = 40
    Terrain.BLOCK = BLOCK
    CHECK_NONE = 0
    CHECK_ANY = 1
    CHECK_TERRAIN = 2

    def __init__(self, x, y):
        super().__init__(x, y)
        self.terrain = None
        self.things = List()

    def __str__(self):
        if not self.terrain:
            return None
        return '[' + super().__str__() + ',' + str(self.terrain.id) + ']'

    def set_terrain(self, terrain):
        self.terrain = Terrain.load_from_name(self * [Tile.BLOCK, Tile.BLOCK], terrain)

    def draw(self, surface):
        if self.terrain:
            self.terrain.draw(surface)

    def draw_objects(self, surface):
        vec = self.get_vec()
        boundary = [vec[0] + Tile.BLOCK / 2, vec[1] + Tile.BLOCK]
        for thing in self.things:
            thing.draw(self, surface, boundary)

    def get_vec(self):
        return [self.x * Tile.BLOCK, self.y * Tile.BLOCK]

    def get_center(self):
        vec = self.get_vec()
        return [vec[0] + Tile.BLOCK / 2, vec[1] + Tile.BLOCK]

    def is_land(self, check):
        land_terrain = self.terrain and self.terrain.type == 1
        land_unit = 0
        for i in self.things:
            if i.collide:
                land_unit = 1
        if check == Tile.CHECK_TERRAIN:
            return land_terrain
        return land_terrain or land_unit
