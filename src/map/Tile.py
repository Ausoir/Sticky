from src.entity.Space import Space
from src.form.Shape import Shape
from src.game import Global
from src.game.Camera import Camera
from src.map.Terrain import Terrain
from src.tools.List import List


class Tile(Space):
    CHECK_NONE = []
    CHECK_ANY = [10, 20, 30, 40]
    CHECK_FIRM = [10, 30]
    CHECK_FOUNDATION = [10, 30, 35]
    CHECK_LARGE = [10, 30, 40]
    CHECK_LANDABLE = [10, 30, 35]
    COLLIDE_FOG = 8
    COLLIDE_BACK = 15
    COLLIDE_TERRAIN = 10
    COLLIDE_OBJECT = 20
    COLLIDE_PROP = 30
    COLLIDE_DOODAD = 35
    COLLIDE_UNIT = 40
    COLLIDE_ITEM = 50
    fog = None

    @staticmethod
    def init():
        Tile.fog = Shape(0, 0, width=Global.BLOCK, height=Global.BLOCK, color=(0, 0, 0, 255))

    def __init__(self, x, y):
        super().__init__(x, y)
        self.frame = 0
        self.terrain = None
        self.things = List()
        self.light = 0

    def __str__(self):
        if self.terrain:
            terrain = str(self.terrain.id)
        else:
            terrain = '-1'
        return '[' + super().__str__() + ',' + terrain + ']'

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

    def draw_overlay(self):
        if self.light <= 0 and Global.draw_group.fade != 0:
            pos = (self.x * Global.BLOCK + Camera.pos[0], self.y * Global.BLOCK + Camera.pos[1])
            Tile.fog.draw()
            # surface.blit(Global.main.overlay, (pos[0], pos[1], Global.BLOCK, Global.BLOCK))
        else:
            self.light -= 1

    def update_light(self, loc):
        self.frame += 1
        if self.frame != loc.update_frame:
            self.light = 0
            self.frame = loc.update_frame

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def get_bottom(self):
        return self.get_vec() + (Global.HALF_BLOCK, Global.BLOCK)

    def is_climbable(self):
        for i in self.things:
            if 'climb' in i.tags:
                return 1
        return 0

    def is_land(self, check):
        if self.terrain:
            if self.terrain.type == 1 and Tile.COLLIDE_TERRAIN in check:
                return 1
            elif self.terrain.type == 3 and Tile.COLLIDE_FOG in check:
                return 1
            elif self.terrain.type == 4 and Tile.COLLIDE_DOODAD in check:
                return 1
        for i in self.things:
            if i.collision_type in check:
                return 1
        return 0

    def to_space(self):
        return Space(self)
