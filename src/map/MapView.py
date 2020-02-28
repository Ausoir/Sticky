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
    display_ratio = .75

    def __init__(self):
        self.update_frame = 0
        self.draw_frame = 0
        self.draw_tiles = [[]]
        self.draw_tiles_min_x = None
        self.draw_tiles_max_x = None
        self.draw_tiles_min_y = None
        self.draw_tiles_max_y = None
        self.tiles = {}
        self.shadows = []
        self.objects = []
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

    def on_sight_change(self):
        for rows in self.draw_tiles:
            for cell in rows:
                cell[2].delete()
        while self.shadows:
            item = self.shadows.pop()
            item.remove()
        Global.land.process_terrain()
        self.draw_tiles.clear()
        pos_x = Camera.target.pos.x
        pos_y = Camera.target.pos.y
        self.view_range_y = MapView.ratio_y(self.view_range)
        self.sight_range_y = MapView.ratio_y(self.sight_range)
        self.draw_tiles_min_x = pos_x - self.sight_range
        self.draw_tiles_max_x = pos_x + self.sight_range
        self.draw_tiles_min_y = pos_y - self.sight_range_y
        self.draw_tiles_max_y = pos_y + self.sight_range_y
        for y in range(-self.sight_range_y, self.sight_range_y + 1):
            row = []
            for x in range(-self.sight_range, self.sight_range + 1):
                pic = Picture(Data.get_cache('g_0x0'), z=-1, group=Global.draw_group.group_tile)
                pic.bound(True)
                row.append([x + pos_x, y + pos_y, pic])
                shade = Shade()
                shade.set_color(self.overlay.weather)
                self.shadows.append(shade)
            self.draw_tiles.append(row)

    def turn(self):
        self.update_frame += 1
        self.update_fog()
        self.overlay.turn()
        if abs(Camera.target.pos.x - self.old_camera.x) > 1 or abs(Camera.target.pos.y - self.old_camera.y) > 1:
            self.on_sight_change()
        self.old_camera = Camera.target.pos

    def update(self):
        self.draw_frame += 1
        index = 0
        for rows in self.draw_tiles:
            for cell in rows:
                this_tile = Global.land.get_tile(cell[0], cell[1])
                if this_tile:
                    this_tile.update_light()
                    if cell[2].visible:
                        if this_tile.light > Turn.rounds * 5:
                            self.shadows[index].set_color(self.overlay.fade)
                        elif this_tile.light > Turn.rounds * 2:
                            c = self.overlay.minimum[:3] + [int(self.overlay.minimum[3]/2)]
                            self.shadows[index].set_color(c)
                        else:
                            self.shadows[index].set_color(self.overlay.minimum)
                vec_x, vec_y = Camera.get_relative_pos(cell[0] * Global.BLOCK,
                                                       cell[1] * Global.BLOCK)
                cell_x = vec_x + Global.OFFSET[0] + Global.HALF_BLOCK
                cell_y = vec_y + Global.OFFSET[1] - Global.HALF_BLOCK
                cell[2].update(x=cell_x, y=cell_y)
                self.shadows[index].update(x=vec_x, y=Global.DISPLAY[1] - vec_y)
                index += 1
        for v in self.objects:
            v.update()

    def update_region(self):
        for i in self.objects:
            if not i.removed:
                i.bound(False)
        self.objects = []
        x = Camera.target.pos.x
        y = Camera.target.pos.y
        extend_x = 0
        extend_y = 0
        index = 0
        for rows in self.draw_tiles:
            for cell in rows:
                if cell[0] - x > self.sight_range:
                    cell[0] = self.draw_tiles_min_x - 1
                    extend_x = -1
                elif cell[0] - x < -self.sight_range:
                    cell[0] = self.draw_tiles_max_x + 1
                    extend_x = 1
                if cell[1] - y > self.sight_range_y:
                    cell[1] = self.draw_tiles_min_y - 1
                    extend_y = -1
                elif cell[1] - y < -self.sight_range_y:
                    cell[1] = self.draw_tiles_max_y + 1
                    extend_y = 1
                key = str(cell[0]) + ',' + str(cell[1])
                tile = self.tiles.get(key)
                if tile:
                    if tile.type == -10:
                        self.shadows[index].shade_walls(tile.joint_neighbors)
                    else:
                        self.shadows[index].remove_shades()
                    cell[2].set(Data.get_cache(tile.get_image()))
                    cell[2].face_direction(tile.direction)
                    cell[2].show(True)
                    row = tile.y - y + self.sight_range_y
                    for thing in tile.things:
                        if not thing.removed:
                            thing.bound(True)
                            thing.set_row(row)
                            self.objects.append(thing)
                else:  # tile is out of bounds
                    self.shadows[index].set_color(self.overlay.weather)
                    self.shadows[index].remove_shades()
                    cell[2].show(False)
                index += 1
        self.draw_tiles_min_x += extend_x
        self.draw_tiles_max_x += extend_x
        self.draw_tiles_min_y += extend_y
        self.draw_tiles_max_y += extend_y

    def update_fog(self):
        center = Global.land.get_tile(Camera.target.pos.x, Camera.target.pos.y)
        self.tiles = {str(Camera.target.pos.x) + ',' + str(Camera.target.pos.y): center}
        max_range = [self.view_range, self.view_range_y]
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
                    tile = Global.land.get_tile(map_x, map_y)
                    if tile:
                        if abs(dx) < self.sight_range and abs(dy) < self.sight_range:
                            in_view_range = abs(tile_x) <= max_range[0] and abs(tile_y) <= max_range[1]
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
                        else:
                            if tile.is_land(Global.player.character.sight) and cell < self.sight_range:
                                blocked = True
                                self.shadow_cast(camera, cell + 1, start, start_slope, flips, max_range, depth + 1)
                                self.new_start = end_slope
            if blocked:
                break
