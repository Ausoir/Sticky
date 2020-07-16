from src.entity.Stock import Stock
from src.game import Global
from src.map.Biome import Biome
from src.map.Location import Location
from src.tools.Data import Data
from src.tools.Space import Space


class World:
    CHUNK = 20
    DEFAULT = [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    ALL = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    BIOME = None
    SEASON = 720

    @staticmethod
    def coord_to_map_name(coord):
        return 'x' + str(coord[0]) + 'y' + str(coord[1])

    @staticmethod
    def get_chunk_coord(cell_num):
        row_start = int(cell_num / 3) * World.CHUNK
        col_start = (cell_num % 3) * World.CHUNK
        return col_start, row_start

    def __init__(self):
        self.location = Location(None)
        self.location.resize(World.CHUNK * 3, World.CHUNK * 3)
        self.cells = None
        self.last_cells = self.cells
        self.dirty = []
        self.map_biome = None
        self.last_spawn = [0, 0, 0, 0, 0, 0, 0, 0, 0]

    def initialize(self, seed, coord_x, coord_y):
        self.map_biome = Biome(seed)
        self.cells = [[i[0] + coord_x, i[1] + coord_y] for i in World.DEFAULT]
        self.load_bubble(World.ALL)

    def save(self):
        self.save_cell(World.ALL)

    def save_cell(self, cells, remove=False):
        for cell_num in cells:
            cell_tiles = []
            cell_objects = []
            cell_roofs = []
            start_coord = World.get_chunk_coord(cell_num)
            is_blank = True
            for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                tile_row = ''
                roof_row = ''
                for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                    tile = self.location.tiles[row][col]
                    icon = tile.get_icon()
                    if icon != '~':
                        is_blank = False
                    tile_row += icon
                    roof_row += str(tile.roof)
                    for thing in tile.things:
                        is_blank = False
                        if thing.save:
                            temp = thing.pos
                            thing.pos = Space(thing.pos.x - start_coord[0], thing.pos.y - start_coord[1])
                            cell_objects.append('[' + thing.__str__() + ']')
                            thing.pos = temp
                        if remove:
                            thing.remove()
                cell_tiles.append(tile_row)
                cell_roofs.append(roof_row)
            if is_blank:
                continue
            if Global.player.player_mode == 0:
                line_1 = '0,0'
            else:
                line_1 = str(Global.player.days) + ',' + str(self.last_spawn[cell_num])
            line_2 = ','.join(cell_objects)
            line_3 = '%'.join(cell_tiles)
            line_4 = '%'.join(cell_roofs)
            write = '\n'.join([line_1, line_2, line_3, line_4])
            map_name = World.coord_to_map_name(self.cells[cell_num])
            Data.write('save/' + map_name + '.map', write)

    def load_bubble(self, added, time=-1):
        obj = []
        for cell_num, cell_coord in enumerate(self.cells):
            map_save_name = 'save/' + World.coord_to_map_name(cell_coord) + '.map'
            map_data_name = 'data/map/' + World.coord_to_map_name(cell_coord) + '.map'
            start_coord = World.get_chunk_coord(cell_num)
            map_is_save = Data.is_file(map_save_name)
            map_is_data = Data.is_file(map_data_name)
            if not map_is_save and not map_is_data:
                for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                    for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                        tile = self.location.tiles[row][col]
                        tile.set_terrain('~')
                        tile.light_source = 0
                        tile.roof = 0
                        tile.light = 0
                        obj += tile.things
            else:
                if map_is_save:
                    map_data = Data.process_raw(Data.read(map_save_name))
                    time_passed = max(0, time - int(map_data[0][0]))
                else:
                    map_data = Data.process_raw(Data.read(map_data_name))
                    time_passed = 24
                self.last_spawn[cell_num] = map_data[0][1]
                terrains = map_data[2][0].split('%')
                roofs = map_data[3][0].split('%')
                for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                    for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                        tile = self.location.tiles[row][col]
                        tile.set_terrain(terrains[y][x])
                        tile.roof = int(roofs[y][x])
                        tile.light_source = 0
                        tile.light = 0
                        obj += tile.things
                renew = Global.player.days - self.last_spawn[cell_num] >= 12
                renew = False
                if cell_num in added:
                    added_props = []
                    for i in map_data[1]:
                        prop = Stock.get(self.location, i[2], i)
                        if not renew or prop.get_value() <= 1:
                            prop.relocate(x=prop.pos.x + start_coord[0], y=prop.pos.y + start_coord[1], force=True)
                            prop.add()
                            added_props.append(prop)
                    if renew:
                        self.last_spawn[cell_num] = int(Global.player.days / 12) * 12
                        savageness = self.get_biome(cell_coord[0], cell_coord[1])
                        for times in range(20 + savageness * 5):
                            x = Global.r.rand_int(start_coord[0], start_coord[0] + World.CHUNK)
                            y = Global.r.rand_int(start_coord[1], start_coord[1] + World.CHUNK)
                            tile = self.location.get_tile(x, y, limit=True)
                            spawn = self.get_spawn(tile.get_name(), level=savageness)
                            if spawn and spawn != 0:
                                from src.map.Tile import Tile
                                if not tile.is_land(Tile.CHECK_ANY):
                                    made = Stock.make(spawn, tile)
                                    made.on_natural_spawn()
                                    if made.get_value() <= 1:
                                        made.tags.set('$', 2)
                        for prop in added_props:
                            prop.on_sleep(time_passed)
        return obj

    def get_spawn(self, habitat, coord_x=0, coord_y=0, level=None):
        if not Global.player.is_daytime():
            spawn_list = World.BIOME.get(habitat + '_night') or World.BIOME.get(habitat)
        else:
            spawn_list = World.BIOME.get(habitat)
        if spawn_list:
            if not isinstance(spawn_list[0], list):
                return Global.r.rand_list(spawn_list)
            if level is None:
                level = self.get_biome(coord_x, coord_y)
            if spawn_list[level]:
                return Global.r.rand_list(spawn_list[level])

    def load_cells(self, x, y):
        new = [[i[0] + x, i[1] + y] for i in World.DEFAULT]
        abandoned = []
        added = []
        for i in range(9):
            if new[i] not in self.cells:
                added.append(i)
            if self.cells[i] not in new:
                abandoned.append(i)
        self.save_cell(abandoned, remove=True)
        self.last_cells = self.cells
        self.cells = new
        return added

    def recenter(self, x, y):
        offset_x = 0
        offset_y = 0
        if x < Global.SIGHT:
            offset_x = -1
        elif y < Global.SIGHT:
            offset_y = -1
        elif x >= self.location.get_width() - Global.SIGHT:
            offset_x = 1
        elif y >= self.location.get_height() - Global.SIGHT:
            offset_y = 1
        else:
            return False
        while self.dirty:
            index = self.dirty.pop()
            self.save_cell([index])
        lights = []
        light_sources = []
        for row in self.location.tiles:
            for tile in row:
                lights.append(tile.light)
                light_sources.append(tile.light_source)
        added = self.load_cells(self.cells[4][0] + offset_x, self.cells[4][1] + offset_y)
        objs = self.load_bubble(added, time=Global.player.days)
        offset_x *= -World.CHUNK
        offset_y *= -World.CHUNK
        for i in objs:
            i.relocate(x=i.pos.x + offset_x, y=i.pos.y + offset_y, force=True)
        index = 0
        width = self.location.get_width()
        height = self.location.get_height()
        for row in range(height):
            if 0 <= row + offset_y < height:
                for col in range(width):
                    if 0 <= col + offset_x < width:
                        self.location.tiles[row + offset_y][col + offset_x].light = lights[index]
                        self.location.tiles[row + offset_y][col + offset_x].light_source = light_sources[index]
                    index += 1
            else:
                index += self.location.get_width()
        self.location.process_terrain()
        return offset_x, offset_y

    def travel(self, coord_x, coord_y, x, y):
        diff_x = coord_x - self.cells[4][0]
        diff_y = coord_y - self.cells[4][1]
        if abs(diff_x) <= 2 and abs(diff_y) <= 2:
            self.recenter(diff_x * World.CHUNK + x, diff_y * World.CHUNK + y)
            Global.player.character.relocate(x=x, y=y, force=True)
            for i in self.location.population.get_all():
                i.bound(False)
        else:
            data = Global.player.character.__str__()
            added = self.load_cells(coord_x, coord_y)
            self.load_bubble(added, time=Global.player.days)
            Global.player.character.load(Data.parse(data))
            Global.player.character.relocate(x=x, y=y, force=True)
            self.location.process_terrain()

    def get_camera_pos(self, x, y):
        chunk = 4
        if x < World.CHUNK:
            chunk = 3
        elif x >= self.location.get_width() - World.CHUNK:
            chunk = 5
        if y < World.CHUNK:
            if chunk == 3:
                chunk = 0
            elif chunk == 5:
                chunk = 2
            else:
                chunk = 1
        elif y >= self.location.get_height() - World.CHUNK:
            if chunk == 3:
                chunk = 6
            elif chunk == 5:
                chunk = 8
            else:
                chunk = 7
        return chunk

    def get_tile_true_pos(self, x, y):
        chunk = self.get_camera_pos(x, y)
        return World.DEFAULT[chunk][0] * World.CHUNK + x, World.DEFAULT[chunk][1] * World.CHUNK + y

    def get_current_chunk(self, x, y):
        chunk = self.get_camera_pos(x, y)
        return self.cells[chunk]

    @staticmethod
    def get_coordinates(x, y):
        chunk = Global.world.get_camera_pos(x, y)
        return Global.world.cells[chunk][0], Global.world.cells[chunk][1]

    def dirty_pos(self, x=None, y=None):
        if x is None or y is None:
            self.dirty = World.ALL
        else:
            chunk = self.get_camera_pos(x, y)
            if chunk not in self.dirty:
                self.dirty.append(chunk)

    def get_biome(self, x, y):
        r = self.map_biome.get_level(x, y)
        r = (r + int(Global.player.days / World.SEASON)) % 4
        return r
