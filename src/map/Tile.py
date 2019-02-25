from src.entity.Space import Space
from src.game import Global
from src.game.Tags import Tags
from src.map.Terrain import Terrain
from src.tools.List import List


class Tile(Space):
    CHECK_NONE = []
    CHECK_ANY = [10, 20, 30, 40]
    CHECK_LARGE = [10, 30, 40]
    CHECK_PROJECTILE = [40, 60]
    CHECK_TERRAIN = [10]
    CHECK_LANDABLE = [10, 30, 32, 40]
    CHECK_CLIMBABLE = [30, 40]
    COLLIDE_TERRAIN = 10
    COLLIDE_OBJECT = 20
    COLLIDE_PROP = 30
    COLLIDE_UNIT = 40
    COLLIDE_ITEM = 50
    COLLIDE_COVER = 60

    def __init__(self, x, y):
        super().__init__(x, y)
        self.terrain = None
        self.things = List()

    def __str__(self):
        if self.terrain:
            terrain = str(self.terrain.id)
        else:
            terrain = '-1'
        return '[' + super().__str__() + ',' + terrain + ']'

    def set_terrain(self, terrain):
        self.terrain = Terrain.load_from_name(self * [Global.BLOCK, Global.BLOCK], terrain)

    def draw(self, surface):
        if self.terrain:
            self.terrain.draw(surface)

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def is_climbable(self):
        if self.terrain and self.terrain.type == 2:
            return 1
        for i in self.things:
            if Tags.climb in i.tags:
                return 1
        return 0

    def is_land(self, check):
        if self.terrain and self.terrain.type % 2:
            if Tile.COLLIDE_TERRAIN in check:
                return 1
        for i in self.things:
            if i.collide in check:
                return 1
        return 0
