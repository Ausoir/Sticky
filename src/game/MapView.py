from src.form.Picture import Picture
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class MapView:
    def __init__(self):
        Turn.add(self.turn)
        self.sight_block = [Tile.COLLIDE_FOG, Tile.COLLIDE_PROP, Tile.COLLIDE_TERRAIN]
        self.update_frame = 0
        self.draw_frame = 0
        self.draw_tiles = []
        self.draw_tiles_min_x = None
        self.draw_tiles_max_x = None
        self.draw_tiles_min_y = None
        self.draw_tiles_max_y = None
        self.fog = {}
        self.tiles = {}
        self.sight_range = 1
        self.view_range = 1
        self.sight_tiles = []
        self.on_resize()

    def on_sight_change(self):
        for i in self.draw_tiles:
            i[2].delete()
        self.draw_tiles.clear()
        pos_x = Camera.target.pos.x
        pos_y = Camera.target.pos.y
        self.draw_tiles_min_x = pos_x - self.sight_range
        self.draw_tiles_max_x = pos_x + self.sight_range
        self.draw_tiles_min_y = pos_y - self.sight_range
        self.draw_tiles_max_y = pos_y + self.sight_range
        for x in range(-self.sight_range, self.sight_range + 1):
            for y in range(-self.sight_range, self.sight_range + 1):
                pic = Picture(Data.get_cache('g_0x1'), group=Global.draw_group.tiles)
                pic.visible = True
                self.draw_tiles.append([x + pos_x, y + pos_y, pic])

    def on_resize(self):
        cols = int(Global.SCREEN_TILES[0] / 2)
        rows = int(Global.SCREEN_TILES[1] / 2)
        self.sight_tiles = [[], []]
        for x in range(-cols, cols + 1):
            for y in range(-rows, 0):
                self.sight_tiles[0].append([x, y])
            for y in range(rows + 1):
                if y != 0 or x != 0:
                    self.sight_tiles[1].append([x, y])

    def turn(self):
        self.update_frame += 1
        self.update_fog()

    def update(self):
        self.draw_frame += 1
        objects = []
        tiles = self.tiles.values()
        for v in tiles:
            for thing in v.things:
                objects.append(thing)
        for i in self.draw_tiles:
            vec_x = i[0] * Global.BLOCK + Camera.pos[0] + Global.HALF_BLOCK
            vec_y = Global.DISPLAY[1] - (i[1] * Global.BLOCK + Camera.pos[1] + Global.HALF_BLOCK)
            i[2].update(x=vec_x, y=vec_y)
        for i in objects:
            i.update()

    def update_fog(self):
        x = Camera.target.pos.x
        y = Camera.target.pos.y
        center = Global.player.location.get_tile(Camera.target.pos)
        center.update_light(self)
        self.tiles = {str(x) + ',' + str(y): center}
        direction = Global.player.character.direction
        start = [x * Global.BLOCK + Global.HALF_BLOCK + (Global.HALF_BLOCK * direction) - direction,
                 y * Global.BLOCK + Global.BLOCK - 1]
        view_y = int(self.view_range * .7)
        for i in self.sight_tiles[0]:
            sight = self.collide_sight(start, i)
            if sight:
                sight.update_light(self)
                if (abs(sight.x - x) < self.view_range and abs(sight.y - y) < view_y) or sight.light:
                    self.tiles[str(sight.x) + ',' + str(sight.y)] = sight
        start[1] = y * Global.BLOCK + 1
        for i in self.sight_tiles[1]:
            sight = self.collide_sight(start, i)
            if sight:
                sight.update_light(self)
                if (abs(sight.x - x) < self.view_range and abs(sight.y - y) < view_y) or sight.light:
                    self.tiles[str(sight.x) + ',' + str(sight.y)] = sight
        extend = 0
        for i in self.draw_tiles:
            if i[0] - x > self.sight_range:
                i[0] = self.draw_tiles_min_x - 1
                extend = -1
            if i[0] - x < -self.sight_range:
                i[0] = self.draw_tiles_max_x + 1
                extend = 1
            key = str(i[0]) + ',' + str(i[1])
            if key in self.tiles:
                tile = self.tiles[key]
                if tile.terrain:
                    i[2].set(tile.terrain.image)
                    i[2].face(tile.terrain.flip_x, tile.terrain.flip_y)
                else:
                    i[2].visible = False
                #     scene_x = i[0] - x + int(Global.SCREEN_TILES[0] / 2)
                #     scene_y = (i[1] - y) + int(Global.SCREEN_TILES[1] / 2)
                #     i[2].set(Data.get_cache('scene_' + str(scene_x) + 'x' + str(scene_y)))
            else:
                i[2].set(Data.get_cache('g_0x1'))
        self.draw_tiles_min_x += extend
        self.draw_tiles_max_x += extend

    def collide_sight(self, vec_from, tile_to):
        abs_x = abs(tile_to[0])
        abs_y = abs(tile_to[1])
        if abs_x >= abs_y:
            sign = 1 if tile_to[0] >= 0 else -1
            if tile_to[1] == 0:
                slope = [abs_x, Global.BLOCK * sign, 0]
            else:
                slope = [abs_x, Global.BLOCK * sign, tile_to[1] / abs_x * Global.BLOCK]
        else:
            sign = 1 if tile_to[1] >= 0 else -1
            if tile_to[0] == 0:
                slope = [abs_y, 0, Global.BLOCK * sign]
            else:
                slope = [abs_y, tile_to[0] / abs_y * Global.BLOCK, Global.BLOCK * sign]
        distance = slope[0]
        current = vec_from
        tile_from = None
        while distance > 0:
            distance -= 1
            current = [current[0] + slope[1], current[1] + slope[2]]
            tile_from = Global.player.location.get_tile_from_vec(current[0], current[1])
            if tile_from.is_land(self.sight_block) and distance > 0:
                return None
        return tile_from

    def set_light(self, light):
        for i in self.tiles.values():
            i.light = light
