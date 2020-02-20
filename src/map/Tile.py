from src.entity.Space import Space
from src.game import Global
from src.game.Camera import Camera
from src.tools import Direction
from src.tools.List import List


class Tile(Space):
    CHECK_NONE = []
    CHECK_ANY = [1, 2, 3, 4, 5, 6, 7]
    CHECK_FIRM = [1, 2, 3, 5]
    CHECK_SIGHT = [1, 2, 6]
    COLLIDE_TERRAIN = 1
    COLLIDE_OBJECT = 2
    COLLIDE_UNIT = 3
    COLLIDE_ITEM = 4
    COLLIDE_WINDOW = 5
    COLLIDE_FOG = 6
    COLLIDE_MAGIC = 7
    DICTIONARY = None

    def __init__(self, location, terrain, x, y):
        super().__init__(x, y)
        self.location = location
        self.terrain = terrain
        data = Tile.DICTIONARY.get(terrain)
        if data:
            self.name = data[0]
            self.image = data[1]
            self.type = data[2]
            self.extend = data[3]
        else:
            self.name = 'None'
            self.image = 'g_0x0'
            self.type = -10
            self.extend = 0
        self.direction = 0
        self.sub_image = None
        self.frame = 0
        self.things = List()
        self.light = 0
        self.shadow = None
        self.joint_neighbors = [0, 0, 0, 0]

    @staticmethod
    def init(arg):
        from src.tools.Dialog import Dialog
        Tile.DICTIONARY = Dialog.to_dict(arg)

    def set_terrain(self, terrain):
        data = Tile.DICTIONARY.get(terrain)
        if data:
            self.terrain = terrain
            self.name = data[0]
            self.image = data[1]
            self.type = data[2]
            self.extend = data[3]
            self.direction = 0
            if self.extend:
                self.sub_image = '0'
            return True

    def get_image(self):
        if self.extend:
            return self.image + self.sub_image
        return self.image

    def get_depth(self):
        if self.terrain:
            if self.type == -10:
                return 2
            return 1
        return 0

    def update_light(self):
        if self.light > 0:
            if self.light > 2:
                for coord in Direction.coord.values():
                    tile = self.get_neighbor(coord[0], coord[1])
                    if tile and tile.light < self.light - 1:
                        if tile.is_land(Tile.CHECK_SIGHT):
                            tile.glow(2)
                        else:
                            tile.glow(self.light - 1)
            self.light = min(3, self.light - 1)

    def update_shader(self):
        if self.type == -10:
            for k, neighbors in Direction.coord.items():
                tile = self.get_neighbor(neighbors[0], neighbors[1])
                if tile and tile.type > -10:
                    self.joint_neighbors[k - 1] = 1
                else:
                    self.joint_neighbors[k - 1] = 0

    def update_update_shader(self):
        for i in Direction.coord.values():
            tile = self.get_neighbor(i[0], i[1])
            if tile:
                tile.update_shader()
        self.update_shader()

    def glow(self, mag):
        self.light = max(mag, self.light)
        diff = (Camera.target.pos - self).abs()
        in_x_range = diff.x > Global.map_view.sight_range > diff.x - self.light + 2
        in_y_range = diff.y > Global.map_view.sight_range_y > diff.y - self.light + 2
        if in_x_range or in_y_range:
            self.update_light()

    def get_neighbor(self, x, y):
        return self.location.get_tile(self.x + x, self.y + y)

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def get_bottom(self):
        return self.get_vec() + (Global.HALF_BLOCK, Global.BLOCK)

    def is_land(self, check):
        if self.type == -11:
            return 1
        elif self.type == -10 and Tile.COLLIDE_TERRAIN in check:
            return 1
        elif self.type == 3 and Tile.COLLIDE_FOG in check:
            return 1
        for i in self.things:
            if i.obstruct_type in check:
                return 1
        return 0

    def to_space(self):
        return Space(self)

    def connect(self):
        if self.extend:
            grid = []
            for coord in Direction.coord.values():
                tile = self.get_neighbor(coord[0], coord[1])
                grid.append(tile is not None and tile.terrain == self.terrain)
            if grid == [True, True, True, True]:
                self.sub_image = '5'
            elif grid == [False, False, False, False]:
                self.sub_image = '0'
            elif grid == [False, True, True, True]:
                self.direction = 1
                self.sub_image = '4'
            elif grid == [True, False, True, True]:
                self.direction = 2
                self.sub_image = '4'
            elif grid == [True, True, False, True]:
                self.direction = 3
                self.sub_image = '4'
            elif grid == [True, True, True, False]:
                self.direction = 4
                self.sub_image = '4'
            elif grid == [True, False, True, False]:
                self.direction = 1
                self.sub_image = '3'
            elif grid == [False, True, False, True]:
                self.direction = 2
                self.sub_image = '3'
            elif grid == [True, False, False, True]:
                self.direction = 1
                self.sub_image = '2'
            elif grid == [True, True, False, False]:
                self.direction = 2
                self.sub_image = '2'
            elif grid == [False, True, True, False]:
                self.direction = 3
                self.sub_image = '2'
            elif grid == [False, False, True, True]:
                self.direction = 4
                self.sub_image = '2'
            elif grid == [True, False, False, False]:
                self.direction = 1
                self.sub_image = '1'
            elif grid == [False, True, False, False]:
                self.direction = 2
                self.sub_image = '1'
            elif grid == [False, False, True, False]:
                self.direction = 3
                self.sub_image = '1'
            elif grid == [False, False, False, True]:
                self.direction = 4
                self.sub_image = '1'
            else:
                print(str(grid) + ' error')
                assert False
