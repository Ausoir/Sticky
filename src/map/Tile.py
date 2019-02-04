from src.entity.Space import Space
from src.game import Global
from src.map.Terrain import Terrain
from src.tools.List import List


class Tile(Space):
    CHECK_NONE = 0
    CHECK_ANY = 1
    CHECK_TERRAIN = 2
    CHECK_UNIT = 3
    CHECK_PROP = 4
    CHECK_ITEM = 5
    CHECK_MEDIUM = [2, 3]
    CHECK_LARGE = [2, 3, 4]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.terrain = None
        self.things = List()

    def __str__(self):
        if self.terrain:
            id = str(self.terrain.id)
        else:
            id = '-1'
        return '[' + super().__str__() + ',' + id + ']'

    def set_terrain(self, terrain):
        self.terrain = Terrain.load_from_name(self * [Global.BLOCK, Global.BLOCK], terrain)

    def draw(self, surface):
        if self.terrain:
            self.terrain.draw(surface)

    def draw_objects(self, surface):
        if self.things:
            vec = self.get_vec()
            boundary = [vec[0] + Global.BLOCK / 2, vec[1] + Global.BLOCK]
            for thing in self.things:
                if thing.pos[0] == self:
                    thing.draw(surface, boundary)

    def get_vec(self):
        return [self.x * Global.BLOCK, self.y * Global.BLOCK]

    def get_center(self):
        vec = self.get_vec()
        return [vec[0] + Global.BLOCK / 2, vec[1] + Global.BLOCK]

    def is_land(self, check):
        if check == Tile.CHECK_NONE:
            return 0
        else:
            if self.terrain and self.terrain.type == 1:
                if isinstance(check, int):
                    if check == Tile.CHECK_TERRAIN:
                        return 1
                else:
                    if Tile.CHECK_TERRAIN in check:
                        return 1
            for i in self.things:
                if isinstance(check, int):
                    if i.collide == check:
                        return 1
                else:
                    if i.collide in check:
                        return 1
