from src.form.Picture import Picture
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Shade import Shade
from src.map.Tile import Tile
from src.tools.Data import Data


class MapView:
    octant_flip = [[1, 0, 0, 1], [0, 1, 1, 0], [0, -1, 1, 0], [-1, 0, 0, 1],
                   [-1, 0, 0, -1], [0, -1, -1, 0], [0, 1, -1, 0], [1, 0, 0, -1]]
    display_ratio = .75

    def __init__(self):
        Turn.add(self.turn)
        Turn.add(self.update_region)
        self.sight_block = [Tile.COLLIDE_FOG, Tile.COLLIDE_OBJECT, Tile.COLLIDE_TERRAIN]
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
        self.new_start = None

    def on_sight_change(self):
        for rows in self.draw_tiles:
            for cell in rows:
                cell[2].delete()
        for i in self.shadows:
            i.remove_overlay()
            i.remove_shader()
        self.shadows = []
        self.draw_tiles.clear()
        pos_x = Camera.target.pos.x
        pos_y = Camera.target.pos.y
        self.sight_range_y = int(self.sight_range * MapView.display_ratio)
        self.draw_tiles_min_x = pos_x - self.sight_range
        self.draw_tiles_max_x = pos_x + self.sight_range
        self.draw_tiles_min_y = pos_y - self.sight_range_y
        self.draw_tiles_max_y = pos_y + self.sight_range_y
        for y in range(-self.sight_range_y, self.sight_range_y + 1):
            row = []
            for x in range(-self.sight_range, self.sight_range + 1):
                pic = Picture(Data.get_cache('g_0x1'), z=-1)
                pic.group = Global.draw_group.group_tile
                pic.show(True)
                pic.bound(True)
                row.append([x + pos_x, y + pos_y, pic])
                self.shadows.append(Shade())
            self.draw_tiles.append(row)

    def turn(self):
        self.update_frame += 1
        self.update_fog()

    def update(self):
        self.draw_frame += 1
        index = 0
        for rows in self.draw_tiles:
            for cell in rows:
                vec_x, vec_y = Camera.get_relative_pos(cell[0] * Global.BLOCK,
                                                       cell[1] * Global.BLOCK)
                cell[2].update(x=vec_x + Global.HALF_BLOCK, y=vec_y - Global.HALF_BLOCK)
                self.shadows[index].update(x=vec_x, y=Global.DISPLAY[1] - vec_y)
                index += 1
        for v in self.tiles.values():
            for thing in v.things:
                thing.update()

    def update_region(self):
        for i in self.objects:
            if not i.removed:
                i.bound(False)
        day = Global.player.is_daytime()
        self.objects = []
        x = Camera.target.pos.x
        y = Camera.target.pos.y
        extend_x = 0
        extend_y = 0
        row = 0
        index = 0
        for rows in self.draw_tiles:
            row += 1
            for cell in rows:
                edge_pass = False
                this_tile = Global.player.location.get_tile((cell[0], cell[1]))
                this_tile.update_light()
                if cell[0] - x > self.sight_range:
                    edge_pass = True
                    cell[0] = self.draw_tiles_min_x - 1
                    extend_x = -1
                elif cell[0] - x < -self.sight_range:
                    edge_pass = True
                    cell[0] = self.draw_tiles_max_x + 1
                    extend_x = 1
                if cell[1] - y > self.sight_range_y:
                    edge_pass = True
                    cell[1] = self.draw_tiles_min_y - 1
                    extend_y = -1
                elif cell[1] - y < -self.sight_range_y:
                    edge_pass = True
                    cell[1] = self.draw_tiles_max_y + 1
                    extend_y = 1
                key = str(cell[0]) + ',' + str(cell[1])
                if key in self.tiles:
                    tile = self.tiles[key]
                    if edge_pass:
                        tile.light = 0
                    if tile.terrain:
                        if not day:
                            self.shadows[index].shade_overlay()
                            if tile.light > 2:
                                self.shadows[index].set_color([0, 0, 0, 0])
                            elif tile.light > 1:
                                c = Global.overlay.weather[:3] + [int(Global.overlay.weather[3]/2)]
                                self.shadows[index].set_color(c)
                            else:
                                if edge_pass:
                                    self.shadows[index].set_color([0, 0, 0, 255])
                                else:
                                    self.shadows[index].set_color(Global.overlay.weather)
                        if tile.terrain.type == 1:
                            self.shadows[index].shade_walls(tile.terrain.joint_neighbors)
                        else:
                            self.shadows[index].remove_shader()
                        cell[2].set(tile.terrain.image)
                        cell[2].show(True)
                        cell[2].face_direction(tile.terrain.direction)
                        for thing in tile.things:
                            if not thing.removed:
                                thing.bound(True)
                                thing.set_row(row)
                                self.objects.append(thing)
                    else:  # tile does not have terrain
                        self.shadows[index].remove_shader()
                        self.shadows[index].set_color([0, 0, 0, 0])
                        cell[2].show(False)
                else:  # tile is out of bounds
                    self.shadows[index].set_color([0, 0, 0, 255])
                    cell[2].show(False)
                index += 1
        self.draw_tiles_min_x += extend_x
        self.draw_tiles_max_x += extend_x
        self.draw_tiles_min_y += extend_y
        self.draw_tiles_max_y += extend_y

    def update_fog(self):
        center = Global.player.location.get_tile(Camera.target.pos)
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
                        if in_view_range or (tile.light and abs(tile_x) <= self.sight_range
                                             and abs(tile_y) <= self.sight_range_y):
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
