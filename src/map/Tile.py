from src.entity.Space import Space
from src.game import Global
from src.game.Camera import Camera
from src.map.Terrain import Terrain
from src.tools.List import List


class Tile(Space):
    CHECK_NONE = []
    CHECK_ANY = [1, 2, 3, 4, 5, 6, 7]
    CHECK_FIRM = [1, 2, 3, 5, 7]
    CHECK_SIGHT = [1, 2, 6]
    COLLIDE_TERRAIN = 1
    COLLIDE_OBJECT = 2
    COLLIDE_UNIT = 3
    COLLIDE_ITEM = 4
    COLLIDE_WINDOW = 5
    COLLIDE_FOG = 6
    COLLIDE_MAGIC = 7

    def __init__(self, loc, x, y):
        super().__init__(x, y)
        self.location = loc
        self.frame = 0
        self.terrain = None
        self.things = List()
        self.light = 0
        self.shadow = None

    def __str__(self):
        if self.terrain:
            terrain = str(self.terrain.id)
        else:
            terrain = '-1'
        return '[' + str(self.x) + ',' + str(self.y) + ',' + terrain + ']'

    def set_terrain(self, terrain):
        self.terrain = Terrain.load_from_name(terrain)
        return self.terrain

    def get_depth(self):
        if self.terrain:
            if self.terrain.type == 1:
                return 2
            return 1
        return 0

    def update(self):
        self.terrain.update()

    def update_light(self):
        if self.light > 0:
            if self.light > 2:
                for coord in [[1, 0], [-1, 0], [0, -1], [0, 1]]:
                    tile = self.get_neighbor(coord[0], coord[1])
                    if tile.light < self.light - 1:
                        if tile.is_land(Tile.CHECK_SIGHT):
                            tile.glow(2)
                        else:
                            tile.glow(self.light - 1)
            self.light = min(3, self.light - 1)

    def glow(self, mag):
        self.light = max(mag, self.light)
        diff = (Camera.target.pos - self).abs()
        in_x_range = diff.x > Global.map_view.sight_range > diff.x - self.light + 2
        in_y_range = diff.y > Global.map_view.sight_range_y > diff.y - self.light + 2
        if in_x_range or in_y_range:
            self.update_light()

    def get_neighbor(self, x, y):
        return self.location.get_tile((self.x + x, self.y + y))

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def get_bottom(self):
        return self.get_vec() + (Global.HALF_BLOCK, Global.BLOCK)

    def is_land(self, check):
        if self.terrain:
            if self.terrain.type == 1 and Tile.COLLIDE_TERRAIN in check:
                return 1
            elif self.terrain.type == 3 and Tile.COLLIDE_FOG in check:
                return 1
        for i in self.things:
            if i.collision_type in check:
                return 1
        return 0

    def to_space(self):
        return Space(self)
