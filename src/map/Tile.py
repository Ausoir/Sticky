from src.entity.Space import Space
from src.form.Shape import Shape
from src.game import Global
from src.game.Camera import Camera
from src.game.Tags import Tags
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
        Tile.fog = Shape(None, (0, 0, 0, 255), Shape.make_rect([Global.BLOCK, Global.BLOCK]))

    def __init__(self, x, y):
        super().__init__(x, y)
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
        self.terrain = Terrain.load_from_name(self * [Global.BLOCK, Global.BLOCK], terrain)
        return self.terrain

    def draw(self, surface):
        if self.terrain:
            if self.terrain.background:
                pos = (self.x * Global.BLOCK + Camera.pos[0], self.y * Global.BLOCK + Camera.pos[1])
                surface.blit(Global.player.background.image, pos,
                             (pos[0], pos[1], Global.BLOCK, Global.BLOCK))
            self.terrain.draw(surface)
        else:
            pos = (self.x * Global.BLOCK + Camera.pos[0], self.y * Global.BLOCK + Camera.pos[1])
            surface.blit(Global.player.background.image, pos,
                         (pos[0], pos[1], Global.BLOCK, Global.BLOCK))

    def draw_overlay(self, surface):
        if self.light <= 0:
            pos = (self.x * Global.BLOCK + Camera.pos[0], self.y * Global.BLOCK + Camera.pos[1])
            surface.blit(Global.main.overlay, (pos[0], pos[1], Global.BLOCK, Global.BLOCK))
        else:
            self.light -= 1

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def get_bottom(self):
        return self.get_vec() + (Global.HALF_BLOCK, Global.BLOCK)

    def is_climbable(self):
        for i in self.things:
            if Tags.climb in i.tags:
                return 1
        return 0

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
