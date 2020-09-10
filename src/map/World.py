from src.entity.Stock import Stock
from src.game import Global
from src.map.Biome import Biome
from src.map.Location import Location
from src.tools.Data import Data


class World:
    CHUNK = 13
    DEFAULT = [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]
    ALL = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    BIOME = None
    SEASON = 240

    @staticmethod
    def coord_to_map_name(coord):
        return 'x' + str(coord[0]) + 'y' + str(coord[1])

    @staticmethod
    def get_chunk_coord(cell_num):
        row_start = int(cell_num / 3) * World.CHUNK
        col_start = (cell_num % 3) * World.CHUNK
        return col_start, row_start

    def __init__(self):
        self.location = Location()
        self.location.resize(World.CHUNK * 3, World.CHUNK * 3)
        self.cells = None
        self.last_cells = self.cells
        self.dirty = False
        self.map_biome = None
        self.cache = {}

    def set_seed(self, seed):
        self.map_biome = Biome(seed)

    def initialize(self, coord_x, coord_y):
        self.cells = [[i[0] + coord_x, i[1] + coord_y] for i in World.DEFAULT]
        self.load_bubble(World.ALL)

    def save(self):
        if not Global.player.character.removed:
            self.save_cell(World.ALL)

    def save_cell(self, cells, remove=False):
        for cell_num in cells:
            cell_tiles = []
            cell_objects = []
            cell_roofs = []
            start_coord = World.get_chunk_coord(cell_num)
            remove_objs = []
            for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                tile_row = ''
                roof_row = ''
                for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                    tile = self.location.tiles[row][col]
                    icon = tile.get_icon()
                    tile_row += icon
                    roof_row += str(tile.roof)
                    for thing in tile.things:
                        if thing.is_save:
                            thing.pos_offset = start_coord
                            cell_objects.append('[' + thing.save() + ']')
                            remove_objs.append(thing)
                cell_tiles.append(tile_row)
                cell_roofs.append(roof_row)
            map_name = World.coord_to_map_name(self.cells[cell_num])
            if remove:
                for i in remove_objs:
                    i.remove()
            if Global.player.player_mode == 0:
                line_1 = '0'
            else:
                line_1 = str(Global.player.days)
            line_2 = ','.join(cell_objects)
            line_3 = '%'.join(cell_tiles)
            line_4 = '%'.join(cell_roofs)
            write = '\n'.join([line_1, line_2, line_3, line_4])
            if map_name in self.cache:
                if remove:
                    del self.cache[map_name]
                else:
                    self.cache[map_name] = Data.process_raw(write)
            Data.write('save/' + map_name + '.map', write)

    def load_cells(self, x, y):
        new = [[i[0] + x, i[1] + y] for i in World.DEFAULT]
        abandoned = []
        added = []
        if self.dirty:
            self.cache = {}
            added = World.ALL
            abandoned = World.ALL
            self.dirty = False
        else:
            for i in range(9):
                if new[i] not in self.cells:
                    added.append(i)
                elif self.cells[i] not in new:
                    abandoned.append(i)
        self.save_cell(abandoned, remove=True)
        self.last_cells = self.cells
        self.cells = new
        return added

    def load_bubble(self, added, time=-1):
        obj = []
        others = []
        explore = 0
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
                        tile.roof = 0
                        tile.light_source = 0
                        tile.light = 0
                        obj += tile.things
                        others += tile.others
            else:
                cache_key = World.coord_to_map_name(cell_coord)
                if cache_key in self.cache:
                    map_data = self.cache[cache_key]
                    time_passed = max(0, time - int(map_data[0][0]))
                elif map_is_save:
                    map_data = Data.process_raw(Data.read(map_save_name))
                    self.cache[cache_key] = map_data
                    time_passed = max(0, time - int(map_data[0][0]))
                else:
                    map_data = Data.process_raw(Data.read(map_data_name))
                    self.cache[cache_key] = map_data
                    time_passed = 8
                if Global.player.player_mode == 0:
                    time_passed = 0
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
                        others += tile.others
                if cell_num in added:
                    renew = time_passed >= 4
                    # renew = False
                    if renew:
                        if not map_is_save:
                            explore += 1
                            Global.player.npc.spawn(start_coord[0], start_coord[1])
                        for i in map_data[1]:
                            prop = Stock.get(i[2], i)
                            if prop.tags.get('$', 0) <= 0:
                                prop.pos = prop.pos.get_neighbor(start_coord[0], start_coord[1])
                                prop.add()
                                prop.on_sleep(time_passed)
                                prop.mutate()
                        self.regrow(cell_coord, start_coord)
                    else:
                        for i in map_data[1]:
                            prop = Stock.get(i[2], i)
                            prop.pos = prop.pos.get_neighbor(start_coord[0], start_coord[1])
                            prop.add()
                            prop.on_sleep(time_passed)
        if Global.player.character:
            Global.player.character.progress_level(min(explore, 4), mode='explore')
        return obj, others

    def regrow(self, cell_coord, start_coord):
        savageness = self.get_biome(cell_coord[0], cell_coord[1])
        for times in range(20):
            x = Global.r.rand_int(start_coord[0], start_coord[0] + World.CHUNK - 1)
            y = Global.r.rand_int(start_coord[1], start_coord[1] + World.CHUNK - 1)
            tile = self.location.get_tile(x, y)
            if tile.get_yield() > -8 and not tile.things:
                spawn = self.get_spawn(tile.get_name(), level=savageness)
                if spawn and spawn != 0:
                    made = Stock.make(spawn, tile)
                    made.on_natural_spawn()
                    if made.get_value() <= 0:
                        made.tags.set('$', 1)

    def regrow_all(self):
        for cell_num, cell_coord in enumerate(self.cells):
            start_coord = World.get_chunk_coord(cell_num)
            self.regrow(cell_coord, start_coord)

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
        lights = []
        light_sources = []
        for row in self.location.tiles:
            for tile in row:
                lights.append(tile.light)
                light_sources.append(tile.light_source)
        added = self.load_cells(self.cells[4][0] + offset_x, self.cells[4][1] + offset_y)
        objs, others = self.load_bubble(added, time=Global.player.days)
        offset_x *= -World.CHUNK
        offset_y *= -World.CHUNK
        for i in objs:
            i.adjust_pos(offset_x, offset_y)
        for i in others:
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

    def travel(self, x, y):
        args = self.get_true_pos_tile(x, y)
        diff_x = args[2] - self.cells[4][0]
        diff_y = args[3] - self.cells[4][1]
        if abs(diff_x) <= 1 and abs(diff_y) <= 1:
            pos = self.get_tile_true_pos(Global.player.character.pos.x, Global.player.character.pos.y)
            pos = Global.player.character.pos.get_neighbor(x - pos[0], y - pos[1])
            Global.player.character.relocate(to=pos, force=True)
            for i in self.location.population.get_all():
                i.bound(False)
        else:
            Global.player.character.deregister()
            self.save_cell(World.ALL, remove=True)
            self.cells = [[i[0] + args[2], i[1] + args[3]] for i in World.DEFAULT]
            self.load_bubble(World.ALL, time=Global.player.days)
            Global.player.character.relocate(x=args[0] + World.CHUNK, y=args[1] + World.CHUNK, force=True)
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

    def get_coordinates(self, x, y):
        chunk = self.get_camera_pos(x, y)
        return self.cells[chunk][0], self.cells[chunk][1]

    def get_tile_true_pos(self, x, y):
        chunk = self.get_camera_pos(x, y)
        coord = self.get_coordinates(x, y)
        r_x = coord[0] * World.CHUNK - World.DEFAULT[chunk][0] * World.CHUNK + x
        r_y = coord[1] * World.CHUNK - World.DEFAULT[chunk][1] * World.CHUNK + y
        return r_x, r_y

    def get_true_pos_tile(self, x, y):
        coord_x = int(x / World.CHUNK) - 1
        coord_y = int(y / World.CHUNK) - 1
        r_x = x % World.CHUNK
        r_y = y % World.CHUNK
        return r_x, r_y, coord_x, coord_y

    def get_biome(self, x, y):
        r = self.map_biome.get_level(x, y)
        r = (r + int(Global.player.days / World.SEASON)) % 4
        return r
