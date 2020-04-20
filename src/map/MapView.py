from src.form.Picture import Picture
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Overlay import Overlay
from src.map.Shade import Shade
from src.tools.Data import Data


class MapView:
    octant_flip = [[1, 0, 0, 1], [0, 1, 1, 0], [0, -1, 1, 0], [-1, 0, 0, 1],
                   [-1, 0, 0, -1], [0, -1, -1, 0], [0, 1, -1, 0], [1, 0, 0, -1]]
    display_ratio = .7

    def __init__(self):
        self.update_frame = 0
        self.draw_frame = 0
        self.draw_tiles = []
        self.tiles = {}
        self.shadows = []
        self.objects = []
        self.others = []
        self.sight_range = 0
        self.sight_range_y = 0
        self.view_range = 0
        self.view_range_y = 0
        self.new_start = None
        self.old_camera = None
        self.overlay = Overlay()

    def on_resize(self):
        self.on_sight_change()

    @staticmethod
    def ratio_y(arg):
        return int(arg * MapView.display_ratio)

    def set_view_range(self, arg):
        self.view_range = arg
        self.view_range_y = MapView.ratio_y(arg)

    def set_sight_range(self, arg):
        self.sight_range = arg
        self.sight_range_y = MapView.ratio_y(arg)

    def on_sight_change(self):
        for pic in self.draw_tiles:
            pic.delete()
        while self.shadows:
            item = self.shadows.pop()
            item.remove()
        Global.land.process_terrain()
        self.draw_tiles.clear()
        for y in range(-self.sight_range_y, self.sight_range_y + 1):
            for x in range(-self.sight_range, self.sight_range + 1):
                pic = Picture(Data.get_cache('g_0x0'), z=-1, group=Global.draw_group.group_tile)
                pic.bound(True)
                shade = Shade()
                self.draw_tiles.append(pic)
                self.shadows.append(shade)
        self.overlay.on_sight_change()
        self.old_camera = Camera.target.pos

    def turn(self):
        self.update_frame += 1
        self.update_fog()
        self.overlay.turn()

    def update(self):
        self.draw_frame += 1
        index = 0
        light_period2 = Turn.rounds * 5
        light_period = Turn.rounds * 2
        cam_x = self.old_camera.x
        cam_y = self.old_camera.y
        for pos_y in range(cam_y-self.sight_range_y, cam_y+self.sight_range_y + 1):
            for pos_x in range(cam_x-self.sight_range, cam_x+self.sight_range + 1):
                this_tile = Global.land.get_tile(pos_x, pos_y)
                if this_tile:
                    this_tile.update_light()
                    if self.draw_tiles[index].visible:
                        if this_tile.light > light_period2:
                            self.shadows[index].set_color(self.overlay.fade)
                        elif this_tile.light > light_period:
                            c = self.overlay.minimum[:3] + [int(self.overlay.minimum[3]/2)]
                            self.shadows[index].set_color(c)
                        else:
                            self.shadows[index].set_color(self.overlay.minimum)
                vec_x, vec_y = Camera.get_relative_pos(pos_x * Global.BLOCK,
                                                       pos_y * Global.BLOCK)
                cell_x = vec_x + Global.OFFSET[0] + Global.HALF_BLOCK
                cell_y = vec_y + Global.OFFSET[1] - Global.HALF_BLOCK
                self.draw_tiles[index].update(x=cell_x, y=cell_y)
                self.shadows[index].update(x=vec_x, y=Global.DISPLAY[1] - vec_y)
                index += 1
        for v in self.objects:
            v.update()
        for v in self.others:
            v.update()

    def update_region(self):
        for i in self.objects:
            if not i.removed:
                i.bound(False)
        for i in self.others:
            i.form.bound(False)
        self.objects = []
        self.others = []
        cam_x = Camera.target.pos.x
        cam_y = Camera.target.pos.y
        index = 0
        for pos_y in range(cam_y-self.sight_range_y, cam_y+self.sight_range_y + 1):
            for pos_x in range(cam_x-self.sight_range, cam_x+self.sight_range + 1):
                key = str(pos_x) + ',' + str(pos_y)
                tile = self.tiles.get(key)
                if tile:
                    if tile.speed == -10:
                        self.shadows[index].shade_walls(tile.joint_neighbors)
                    else:
                        self.shadows[index].remove_shades()
                    self.draw_tiles[index].set(Data.get_cache(tile.get_image()))
                    self.draw_tiles[index].face_direction(tile.direction)
                    self.draw_tiles[index].show(True)
                    row = tile.y - cam_y + self.sight_range_y
                    for thing in tile.things:
                        if not thing.removed:
                            thing.bound(True)
                            thing.set_row(row)
                            self.objects.append(thing)
                    for thing in tile.others:
                        thing.form.bound(True)
                        self.others.append(thing)
                else:  # tile is out of bounds
                    self.shadows[index].set_color([0, 0, 0, 255])
                    self.shadows[index].remove_shades()
                    self.draw_tiles[index].show(False)
                index += 1
        self.old_camera = Camera.target.pos

    def update_fog(self):
        center = Global.land.get_tile(Camera.target.pos.x, Camera.target.pos.y)
        self.tiles = {str(Camera.target.pos.x) + ',' + str(Camera.target.pos.y): center}
        for i in range(8):
            self.shadow_cast(Camera.target.pos, 1, 1.0, 0.0, self.octant_flip[i], 0)

    def shadow_cast(self, camera, row, start, end, flips, depth):
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
                    tile = Global.land.get_tile(map_x, map_y)
                    if tile:
                        if abs(dx) < self.sight_range + 1 and abs(dy) < self.sight_range + 1:
                            in_view_range = abs(tile_x) <= self.view_range and abs(tile_y) <= self.view_range_y
                            if in_view_range or (tile.light and abs(tile_x) <= self.sight_range
                                                 and abs(tile_y) <= self.sight_range_y):
                                self.tiles[str(map_x) + ',' + str(map_y)] = tile
                        if blocked:
                            if tile.is_land(Global.player.character.sight):
                                self.new_start = end_slope
                                continue
                            else:
                                blocked = False
                                start = self.new_start
                        elif tile.is_land(Global.player.character.sight) and cell < self.sight_range:
                            blocked = True
                            self.shadow_cast(camera, cell + 1, start, start_slope, flips, depth + 1)
                            self.new_start = end_slope
            if blocked:
                break
