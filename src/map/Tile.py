from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.tools.List import List
from src.tools.Space import Space


class Tile(Space):
    CHECK_NONE = []
    CHECK_ANY = [1, 2, 3, 4, 5, 6, 7]
    CHECK_FIRM = [3, 5, 6, 7]
    CHECK_SIGHT = [2, 5, 6, 7]
    COLLIDE_MAGIC = 7
    COLLIDE_TERRAIN = 6
    COLLIDE_OBJECT = 5
    COLLIDE_WINDOW = 4
    COLLIDE_UNIT = 3
    COLLIDE_FOG = 2
    COLLIDE_ITEM = 1
    DATA = None
    DICTIONARY = {}

    @staticmethod
    def init(data):
        Tile.DATA = data
        for count, line in enumerate(data):
            Tile.DICTIONARY[line[0]] = count

    @staticmethod
    def get_collision_by_name(num):
        if num == Tile.COLLIDE_TERRAIN:
            return 'Terrain'
        elif num == Tile.COLLIDE_OBJECT:
            return 'Object'
        elif num == Tile.COLLIDE_UNIT:
            return 'Unit'
        elif num == Tile.COLLIDE_ITEM:
            return 'Item'
        elif num == Tile.COLLIDE_WINDOW:
            return 'Window'
        elif num == Tile.COLLIDE_FOG:
            return 'Fog'
        elif num == Tile.COLLIDE_MAGIC:
            return 'Magic'

    def __init__(self, location, terrain, x, y):
        super().__init__(x, y)
        self.location = location
        self.index = 0
        self.set_terrain(terrain)
        self.direction = 0
        self.sub_image = None
        self.things = List()
        self.others = List()
        self.roof = 0
        self.light = 0
        self.light_source = 0
        self.joint_neighbors = [0, 0, 0, 0]
        self.sight_frame = 0

    def is_seen(self):
        return self.sight_frame == Global.map_view.sight_frame

    def set_terrain(self, terrain):
        data = Tile.DICTIONARY.get(terrain)
        if data is not None:
            self.set_index(data)
            return True

    def set_index(self, index):
        self.index = index
        self.direction = 0
        if self.get_extend() > 0:
            self.sub_image = 0

    def get_face(self, pos):
        diff = pos - self
        horizontal = abs(diff.x) >= abs(diff.y)
        if horizontal:
            if diff.x < 0:
                direction = 1
            else:
                direction = 3
        else:
            if diff.y < 0:
                direction = 2
            else:
                direction = 0
        return direction

    def get_icon(self):
        return Tile.DATA[self.index][0]

    def get_name(self):
        return Tile.DATA[self.index][1]

    def get_image_set(self):
        return Tile.DATA[self.index][2]

    def get_yield(self):
        return Tile.DATA[self.index][3]

    def get_extend(self):
        return Tile.DATA[self.index][4]

    def get_shader(self):
        return Tile.DATA[self.index][5]

    def get_hardness(self):
        return Tile.DATA[self.index][6]

    def get_tags(self):
        return Tile.DATA[self.index][7]

    def has_tag(self, tag):
        return tag in self.get_tags()

    def get_image(self):
        r = self.get_image_set()
        if isinstance(r, list):
            return r[self.sub_image]
        return r

    def update_shader(self):
        if self.get_shader() == 1:
            for k, c in enumerate(Global.cardinal_coord):
                tile = self.get_neighbor(c[0], c[1])
                if tile and tile.get_shader() == 0:
                    self.joint_neighbors[k - 1] = 1
                else:
                    self.joint_neighbors[k - 1] = 0

    def update_update_shader(self):
        for i in Global.cardinal_coord:
            tile = self.get_neighbor(i[0], i[1])
            if tile:
                tile.update_shader()
        self.update_shader()

    def update_light(self):
        if self.light_source > 0:
            self.light_source -= 1
        else:
            if self.light > 0:
                self.light -= 1
            for coord in Global.cardinal_coord:
                tile = self.get_neighbor(coord[0], coord[1])
                if tile:
                    diminish = tile.light - 1
                    if diminish > self.light:
                        if not tile.is_land(Tile.CHECK_SIGHT):
                            self.light = diminish

    def glow(self, mag):
        self.light = min(13, max(mag, self.light))
        self.light_source = Turn.rounds
        diff = (Camera.target.pos - self).abs()
        if diff.x > Global.map_view.sight_range or diff.y > Global.map_view.sight_range_y:
            self.glow_reach(mag * Turn.rounds)

    def glow_reach(self, prev_diff):
        if self.light > 0:
            diff = (Camera.target.pos - self).abs()
            current_diff = diff.sum()
            if current_diff < prev_diff:
                dist = int(self.light / Turn.rounds) - 1
                in_x_range = diff.x < Global.map_view.sight_range + dist
                in_y_range = diff.y < Global.map_view.sight_range_y + dist
                if in_x_range or in_y_range:
                    for coord in Global.cardinal_coord:
                        tile = self.get_neighbor(coord[0], coord[1])
                        if tile and tile.light == 0:
                            tile.update_light()
                            tile.glow_reach(current_diff)

    def glow_stop(self):
        if self.light > 7:
            radius = min(7, self.light - 7)
            for neighbor in self.get_area(radius, radius):
                neighbor.light = 0
                neighbor.light_source = 0
        self.light_source = 0
        self.light = 0

    def get_neighbor(self, x, y, limit=False):
        return self.location.get_tile(self.x + x, self.y + y, limit=limit)

    def get_cardinal(self, direction, distance=1, limit=True):
        coord = Global.cardinal_coord[direction % 4]
        return self.location.get_tile(self.x + coord[0] * distance, self.y + coord[1] * distance, limit=limit)

    def get_area(self, range_x, range_y):
        tiles = []
        for x in range(-range_x, range_x+1):
            for y in range(-range_y, range_y+1):
                tile = self.location.get_tile(self.x + x, self.y + y)
                if tile:
                    tiles.append(tile)
        return tiles

    def get_vec(self):
        return self * Global.BLOCK

    def get_center(self):
        return self.get_vec() + Global.HALF_BLOCK

    def get_bottom(self):
        return self.get_vec() + (Global.HALF_BLOCK, Global.BLOCK)

    def is_land(self, check):
        tile_yield = self.get_yield()
        if tile_yield == -99:
            return 1
        elif tile_yield == -10 and Tile.COLLIDE_TERRAIN in check:
            return 1
        elif tile_yield == -9 and Tile.COLLIDE_WINDOW in check:
            return 1
        elif tile_yield == -8 and Tile.COLLIDE_FOG in check:
            return 1
        for i in self.things:
            if i.obstruct_type in check:
                return 1
        return 0

    def get_landscapes(self):
        lands = []
        yld = self.get_yield()
        if yld == -10:
            lands.append(Tile.COLLIDE_TERRAIN)
        elif yld == -9:
            lands.append(Tile.COLLIDE_WINDOW)
        elif yld == -8:
            lands.append(Tile.COLLIDE_FOG)
        for i in self.things:
            if i.obstruct_type not in lands:
                lands.append(i.obstruct_type)
        return lands

    def get_solidity(self):
        yld = self.get_yield()
        most = 0
        for i in self.things:
            most = max(most, i.obstruct_type)
        if yld == -10:
            most = max(most, Tile.COLLIDE_TERRAIN)
        elif yld == -9:
            most = max(most, Tile.COLLIDE_WINDOW)
        elif yld == -8:
            most = max(most, Tile.COLLIDE_FOG)
        elif yld == -99:
            most = 7
        return most

    def get_move_speed(self):
        total = self.get_yield()
        for i in self.things:
            move = i.tags.get('spd')
            if move:
                total += move
        return total

    def connect(self):
        if self.get_extend() != 0:
            def fn(tile):
                return tile is None or tile.get_extend() == self.get_extend()
            connection, direction = Tile.get_connection(self, fn)
            self.sub_image = connection
            self.direction = direction

    def connect_connect(self):
        for i in Global.cardinal_coord:
            neighbor = self.get_neighbor(i[0], i[1])
            if neighbor:
                neighbor.connect()
        self.connect()

    @staticmethod
    def get_connection(self, fn):
        grid = []
        for coord in Global.cardinal_coord:
            tile = self.get_neighbor(coord[0], coord[1])
            grid.append(fn(tile))
        connection, direction = 0, 0
        if grid == [True, True, True, True]:
            connection = 5
        elif grid == [True, False, True, True]:
            direction = 1
            connection = 4
        elif grid == [True, True, False, True]:
            direction = 2
            connection = 4
        elif grid == [True, True, True, False]:
            direction = 3
            connection = 4
        elif grid == [False, True, True, True]:
            direction = 0
            connection = 4
        elif grid == [False, True, False, True]:
            direction = 1
            connection = 2
        elif grid == [True, False, True, False]:
            direction = 2
            connection = 2
        elif grid == [True, True, False, False]:
            direction = 1
            connection = 3
        elif grid == [False, True, True, False]:
            direction = 2
            connection = 3
        elif grid == [False, False, True, True]:
            direction = 3
            connection = 3
        elif grid == [True, False, False, True]:
            direction = 0
            connection = 3
        elif grid == [False, True, False, False]:
            direction = 1
            connection = 1
        elif grid == [False, False, True, False]:
            direction = 2
            connection = 1
        elif grid == [False, False, False, True]:
            direction = 3
            connection = 1
        elif grid == [True, False, False, False]:
            direction = 0
            connection = 1
        return connection, direction
