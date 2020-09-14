from src.form.Picture import Picture
from src.game import Global
from src.game.Camera import Camera
from src.map.Overlay import Overlay
from src.map.Shade import Shade
from src.tools.Data import Data


class MapView:
    octant_flip = [[1, 0, 0, 1], [0, 1, 1, 0], [0, -1, 1, 0], [-1, 0, 0, 1],
                   [-1, 0, 0, -1], [0, -1, -1, 0], [0, 1, -1, 0], [1, 0, 0, -1]]
    display_ratio = .8

    def __init__(self):
        self.sight_frame = 0
        self.draw_frame = 0
        self.draw_tiles = []
        self.shadows = []
        self.in_bounds = []
        self.sight_range = 0
        self.sight_range_y = 0
        self.view_range = 0
        self.view_range_y = 0
        self.brightness = 0
        self.new_start = None
        self.old_camera = None
        self.overlay = Overlay()
        from src.form.Shape import Shape
        self.tape = Shape(-Global.CENTER[0], 160, 800, Global.draw_group.group_gui,
                          width=Global.DISPLAY[0] - Global.BLOCK * 2, height=Global.BLOCK, color=[0, 0, 0, 255])
        self.tape.add_batch()
        self.tape.show(True)

    @staticmethod
    def ratio_y(arg):
        return int(arg * MapView.display_ratio)

    def set_view_range(self, arg):
        self.view_range = arg
        self.view_range_y = self.ratio_y(arg)

    def set_sight_range(self, arg):
        self.sight_range = arg
        self.sight_range_y = self.ratio_y(arg)

    def on_sight_change(self):
        for pic in self.draw_tiles:
            pic.delete()
        while self.shadows:
            item = self.shadows.pop()
            item.remove()
        Global.world.location.process_terrain()
        self.draw_tiles.clear()
        for y in range(-self.sight_range_y, self.sight_range_y + 1):
            for x in range(-self.sight_range, self.sight_range + 1):
                pic = Picture(Data.graphics['g'][0][0], z=-1, group=Global.draw_group.group_tile)
                pic.bound(True)
                shade = Shade()
                self.draw_tiles.append(pic)
                self.shadows.append(shade)
        self.old_camera = Camera.target.pos

    def turn(self):
        brightness = Global.map_view.overlay.LIGHT[Global.player.days % 24]
        if self.brightness != brightness:
            self.brightness = brightness
            self.reset_lighting()
        self.update_fog()
        self.overlay.turn()

    def reset_lighting(self):
        for rows in Global.world.location.tiles:
            for cell in rows:
                if cell.light_source == 0:
                    if cell.roof == 0:
                        cell.light = self.brightness
                    else:
                        cell.light = 0

    def update_region_editor(self):
        cam_x = Camera.target.pos.x
        cam_y = Camera.target.pos.y
        index = 0
        for pos_y in range(cam_y-self.sight_range_y, cam_y+self.sight_range_y + 1):
            for pos_x in range(cam_x-self.sight_range, cam_x+self.sight_range + 1):
                this_tile = Global.world.location.get_tile(pos_x, pos_y)
                if this_tile:
                    if this_tile.roof == 0:
                        self.shadows[index].set_color([120, 0, 0, 40])
                    else:
                        self.shadows[index].set_color([250, 250, 0, 60])
                    self.shadows[index].overlay.update()
                index += 1

    def update(self):
        self.draw_frame += 1
        index = 0
        cam_x = self.old_camera.x
        cam_y = self.old_camera.y
        dim_light = self.overlay.get_dim_light()
        col_range = [max(0, cam_x-self.sight_range),
                     min(Global.world.location.get_width()-1, cam_x+self.sight_range)]
        row_range = [max(0, cam_y-self.sight_range_y),
                     min(Global.world.location.get_height()-1, cam_y+self.sight_range_y)]
        for pos_y in range(row_range[0], row_range[1] + 1):
            for pos_x in range(col_range[0], col_range[1] + 1):
                this_tile = Global.world.location.tiles[pos_y][pos_x]
                if this_tile:
                    if this_tile.roof == 0:
                        this_tile.light = max(this_tile.light, self.brightness)
                    this_tile.update_light()
                    in_screen = row_range[0] <= pos_y <= row_range[1] and col_range[0] <= pos_x <= col_range[1]
                    if in_screen:
                        if self.draw_tiles[index].visible:
                            if this_tile.light > 7:
                                self.shadows[index].set_color(self.overlay.fade)
                            elif this_tile.light > 4:
                                self.shadows[index].set_color(dim_light)
                            else:
                                self.shadows[index].set_color(self.overlay.minimum)
                            for thing in this_tile.things:
                                thing.update()
                            for thing in this_tile.others:
                                thing.update()
                        vec_x, vec_y = Camera.get_relative_pos(pos_x * Global.BLOCK,
                                                               pos_y * Global.BLOCK)
                        self.draw_tiles[index].place(vec_x + Global.HALF_BLOCK, vec_y - Global.HALF_BLOCK)
                        self.shadows[index].update(x=vec_x, y=Global.DISPLAY[1] - vec_y)
                        index += 1
        tx = self.draw_tiles[0].x - Global.OFFSET[0] - Global.BLOCK
        ty = Global.DISPLAY[1] - (self.draw_tiles[0].y - Global.OFFSET[1]) - Global.HALF_BLOCK - Global.BLOCK
        self.tape.update(x=tx, y=ty)

    def update_region(self):
        for i in self.in_bounds:
            for thing in i.things:
                thing.bound(False)
            for thing in i.others:
                thing.form.bound(False)
        self.in_bounds = []
        cam_x = Camera.target.pos.x
        cam_y = Camera.target.pos.y
        index = 0
        col_range = [cam_x-self.sight_range, cam_x+self.sight_range]
        row_range = [cam_y-self.sight_range_y, cam_y+self.sight_range_y]
        for pos_y in range(row_range[0], row_range[1] + 1):
            for pos_x in range(col_range[0], col_range[1] + 1):
                this_tile = Global.world.location.get_tile(pos_x, pos_y)
                if this_tile and this_tile.is_seen():
                    if this_tile.get_shader() == 1:
                        self.shadows[index].shade_walls(this_tile.joint_neighbors)
                    else:
                        self.shadows[index].remove_shades()
                    self.draw_tiles[index].set(Data.get_graphics(this_tile.get_image()))
                    self.draw_tiles[index].face(this_tile.direction)
                    self.draw_tiles[index].show(True)
                    self.shadows[index].show(True)
                    row = this_tile.y - cam_y + self.sight_range_y
                    self.in_bounds.append(this_tile)
                    for thing in this_tile.things:
                        thing.bound(True)
                        thing.set_row(row)
                    for thing in this_tile.others:
                        thing.form.bound(True)
                else:
                    self.shadows[index].set_color([0, 0, 0, 255])
                    self.shadows[index].remove_shades()
                    # self.shadows[index].show(False)
                    self.draw_tiles[index].show(False)
                index += 1
        self.old_camera = Camera.target.pos

    def update_fog(self):
        self.sight_frame += 1
        center = Global.world.location.get_tile(Camera.target.pos.x, Camera.target.pos.y)
        for i in range(8):
            self.shadow_cast(Camera.target.pos, 1, 1.0, 0.0, self.octant_flip[i], 0)
        center.sight_frame = self.sight_frame

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
                    tile = Global.world.location.get_tile(map_x, map_y)
                    if tile:
                        if abs(dx) < self.sight_range + 1 and abs(dy) < self.sight_range + 1:
                            in_view_range = abs(tile_x) <= self.view_range and abs(tile_y) <= self.view_range_y
                            if in_view_range or (tile.light and abs(tile_x) <= self.sight_range
                                                 and abs(tile_y) <= self.sight_range_y):
                                tile.sight_frame = self.sight_frame
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
