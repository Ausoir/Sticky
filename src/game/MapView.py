from src.form.Picture import Picture
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class MapView:
    octant_flip = [[1, 0, 0, 1], [0, 1, 1, 0], [0, -1, 1, 0], [-1, 0, 0, 1],
                   [-1, 0, 0, -1], [0, -1, -1, 0], [0, 1, -1, 0], [1, 0, 0, -1]]
    display_ratio = .75

    def __init__(self):
        Turn.add(self.turn)
        Turn.add(self.update_region)
        self.sight_block = [Tile.COLLIDE_FOG, Tile.COLLIDE_PROP, Tile.COLLIDE_TERRAIN]
        self.update_frame = 0
        self.draw_frame = 0
        self.draw_tiles = []
        self.draw_tiles_min_x = None
        self.draw_tiles_max_x = None
        self.draw_tiles_min_y = None
        self.draw_tiles_max_y = None
        self.tiles = {}
        self.objects = []
        self.sight_range = 1
        self.view_range = 1
        self.new_start = None

    def on_sight_change(self):
        for i in self.draw_tiles:
            i[2].delete()
        self.draw_tiles.clear()
        pos_x = Camera.target.pos.x
        pos_y = Camera.target.pos.y
        sight_range_y = int(self.sight_range * MapView.display_ratio)
        self.draw_tiles_min_x = pos_x - self.sight_range
        self.draw_tiles_max_x = pos_x + self.sight_range
        self.draw_tiles_min_y = pos_y - sight_range_y
        self.draw_tiles_max_y = pos_y + sight_range_y
        for x in range(-self.sight_range, self.sight_range + 1):
            for y in range(-sight_range_y, sight_range_y + 1):
                pic = Picture(Data.get_cache('g_0x1'), group=Global.draw_group.tiles)
                pic.show(True)
                pic.add_batch(True)
                self.draw_tiles.append([x + pos_x, y + pos_y, pic])

    def turn(self):
        self.update_frame += 1
        self.update_fog()

    def update(self):
        self.draw_frame += 1
        for i in self.objects:
            if not i.removed:
                i.add_batch(False)
        self.objects = []
        tiles = self.tiles.values()
        for v in tiles:
            for thing in v.things:
                self.objects.append(thing)
        for i in self.draw_tiles:
            vec_x = i[0] * Global.BLOCK + Camera.pos[0] + Global.HALF_BLOCK
            vec_y = Global.DISPLAY[1] - (i[1] * Global.BLOCK + Camera.pos[1] + Global.HALF_BLOCK)
            i[2].update(x=vec_x, y=vec_y)
        for i in self.objects:
            if not i.removed:
                i.update()
                i.add_batch(True)

    def update_region(self):
        x = Camera.target.pos.x
        y = Camera.target.pos.y
        extend_x = 0
        extend_y = 0
        sight_range_y = int(self.sight_range * MapView.display_ratio)
        for i in self.draw_tiles:
            if i[0] - x > self.sight_range:
                i[0] = self.draw_tiles_min_x - 1
                extend_x = -1
            elif i[0] - x < -self.sight_range:
                i[0] = self.draw_tiles_max_x + 1
                extend_x = 1
            if i[1] - y > sight_range_y:
                i[1] = self.draw_tiles_min_y - 1
                extend_y = -1
            elif i[1] - y < -sight_range_y:
                i[1] = self.draw_tiles_max_y + 1
                extend_y = 1
            key = str(i[0]) + ',' + str(i[1])
            if key in self.tiles:
                tile = self.tiles[key]
                if tile.terrain:
                    i[2].set(tile.terrain.image)
                    i[2].reset()
                    i[2].face(tile.terrain.flip_x, tile.terrain.flip_y)
            else:
                i[2].set(Data.get_cache('g_0x1'))
        self.draw_tiles_min_x += extend_x
        self.draw_tiles_max_x += extend_x
        self.draw_tiles_min_y += extend_y
        self.draw_tiles_max_y += extend_y

    def update_fog(self):
        center = Global.player.location.get_tile(Camera.target.pos)
        center.update_light(self)
        self.tiles = {str(Camera.target.pos.x) + ',' + str(Camera.target.pos.y): center}
        max_range = [self.view_range, int(self.view_range * MapView.display_ratio)]
        for i in range(8):
            self.shadow_cast(Camera.target.pos, 1, 1.0, 0.0, self.octant_flip[i], max_range, 0)

    def shadow_cast(self, camera, row, start, end, flips, max_range, depth):
        if start < end:
            return
        for cell in range(row, self.sight_range + 1):
            dx, dy = -cell - 1, -cell
            blocked = False
            while dx <= 0:
                dx += 1
                start_slope, end_slope = (dx - 0.5) / (dy + 0.5), (dx + 0.5) / (dy - 0.5)
                if start < end_slope:
                    continue
                elif end > start_slope:
                    break
                else:
                    tile_x = dx * flips[0] + dy * flips[1]
                    tile_y = dx * flips[2] + dy * flips[3]
                    map_x = camera.x + tile_x
                    map_y = camera.y + tile_y
                    tile = Global.player.location.get_tile([map_x, map_y])
                    if abs(dx) < self.sight_range and abs(dy) < self.sight_range:
                        in_view_range = abs(tile_x) <= max_range[0] and abs(tile_y) <= max_range[1]
                        sight_range_y = int(self.sight_range * MapView.display_ratio)
                        if in_view_range or (tile.light and abs(tile_x) <= self.sight_range
                                             and abs(tile_y) <= sight_range_y):
                            self.tiles[str(map_x) + ',' + str(map_y)] = tile
                    if blocked:
                        if tile.is_land(self.sight_block):
                            self.new_start = end_slope
                            continue
                        else:
                            blocked = False
                            start = self.new_start
                    else:
                        if tile.is_land(self.sight_block) and cell < self.sight_range:
                            blocked = True
                            self.shadow_cast(camera, cell + 1, start, start_slope, flips, max_range, depth + 1)
                            self.new_start = end_slope
            if blocked:
                break

    def collide_sight(self, vec_from, slope):
        distance = slope[0]
        current = vec_from
        tile_from = []
        while distance > 0:
            distance -= 1
            current = [current[0] + slope[1], current[1] + slope[2]]
            tile = Global.player.location.get_tile_from_vec(current[0], current[1])
            tile_from.append(tile)
            if tile.is_land(self.sight_block) and distance > 0:
                break
        return tile_from

    def set_light(self, light):
        for i in self.tiles.values():
            i.light = light
