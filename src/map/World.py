from src.game import Global
from src.map.Location import Location
from src.tools.Data import Data
from src.tools.Space import Space


class World:
    CHUNK = 20
    DEFAULT = [[-1, -1], [0, -1], [1, -1], [-1, 0], [0, 0], [1, 0], [-1, 1], [0, 1], [1, 1]]

    @staticmethod
    def coord_to_map_name(coord):
        return 'x' + str(coord[0]) + 'y' + str(coord[1])

    @staticmethod
    def get_chunk_coord(cell_num):
        row_start = int(cell_num / 3) * World.CHUNK
        col_start = (cell_num % 3) * World.CHUNK
        return col_start, row_start

    def __init__(self, map_name, coord_x, coord_y):
        self.location = Location(map_name, None)
        self.location.resize(World.CHUNK * 3, World.CHUNK * 3)
        self.cells = [[i[0] + coord_x, i[1] + coord_y] for i in World.DEFAULT]
        self.last_cells = self.cells
        self.load_bubble([0, 1, 2, 3, 4, 5, 6, 7, 8])
        self.dirty = []

    def save(self):
        self.save_cell([0, 1, 2, 3, 4, 5, 6, 7, 8])

    def save_cell(self, cells, remove=False):
        for cell_num in cells:
            cell_tiles = []
            cell_objects = []
            cell_roofs = []
            start_coord = World.get_chunk_coord(cell_num)
            for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                tile_row = ''
                roof_row = ''
                for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                    tile = self.location.tiles[row][col]
                    tile_row += tile.terrain
                    roof_row += tile.roof
                    for thing in tile.things:
                        if thing.save:
                            temp = thing.pos
                            thing.pos = Space(thing.pos.x - start_coord[0], thing.pos.y - start_coord[1])
                            cell_objects.append('[' + thing.__str__() + ']')
                            thing.pos = temp
                        if remove:
                            thing.remove()
                cell_tiles.append(tile_row)
                cell_roofs.append(roof_row)
            line_1 = self.location.tags.__str__()
            line_2 = ','.join(cell_objects)
            line_3 = '%'.join(cell_tiles)
            line_4 = '%'.join(cell_roofs)
            write = '\n'.join([line_1, line_2, line_3, line_4])
            print('saving ' + str(cell_num))
            map_name = World.coord_to_map_name(self.cells[cell_num])
            Data.write('save/' + map_name + '.map', write)

    def load_bubble(self, added):
        from src.entity.Stock import Stock
        obj = []
        for count, cell_coord in enumerate(self.cells):
            map_save_name = 'save/' + World.coord_to_map_name(cell_coord) + '.map'
            map_data_name = 'data/map/world/' + World.coord_to_map_name(cell_coord) + '.map'
            start_coord = World.get_chunk_coord(count)
            map_is_save = Data.is_file(map_save_name)
            map_is_data = Data.is_file(map_data_name)
            if not map_is_save and not map_is_data:
                for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                    for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                        tile = self.location.tiles[row][col]
                        tile.set_terrain('~')
                        tile.light_source = 0
                        tile.light = 0
                        obj += tile.things
            else:
                if map_is_save:
                    map_data = Data.process_raw(Data.read(map_save_name))
                else:
                    map_data = Data.process_raw(Data.read(map_data_name))
                terrains = map_data[2][0].split('%')
                roofs = map_data[3][0].split('%')
                for y, row in enumerate(range(start_coord[1], start_coord[1] + World.CHUNK)):
                    for x, col in enumerate(range(start_coord[0], start_coord[0] + World.CHUNK)):
                        tile = self.location.tiles[row][col]
                        tile.set_terrain(terrains[y][x])
                        tile.roof = roofs[y][x]
                        tile.light_source = 0
                        tile.light = 0
                        obj += tile.things
                if count in added:
                    for i in map_data[1]:
                        prop = Stock.get(self.location, i[2], i)
                        prop.relocate(x=prop.pos.x + start_coord[0], y=prop.pos.y + start_coord[1], force=True)
                        prop.add()
        return obj

    def push_cell(self, x, y):
        new = [[i[0] + x, i[1] + y] for i in self.cells]
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
        added = self.push_cell(offset_x, offset_y)
        objs = self.load_bubble(added)
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
        return offset_x, offset_y

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
        start_coord = World.get_chunk_coord(chunk)
        return chunk, start_coord

    def dirty_pos(self, x, y):
        chunk, start_coord = self.get_camera_pos(x, y)
        if chunk not in self.dirty:
            self.dirty.append(chunk)
