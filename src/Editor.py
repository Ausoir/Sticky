import sys

import pygame

from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn
from src.tools.Data import Data


class Editor:
    scroll = 20

    def __init__(self, loc, control):
        def update():
            control.turn()
        self.backup = Turn.update
        Turn.update = update
        Group.effects.append(self)
        control.set_keymap('data/editor_keymap.txt')
        control.player = self
        self.control = control
        self.location = loc
        self.font = pygame.font.SysFont('Helvetica', 20)
        self.visible = 1
        self.mouse = [0, 0]
        self.tool = ToolTerrain(self.location)
        self.display_text = ''
        self.enter = 0
        self.prev_command = None
        Camera.target = Camera.target + 0

    def remove(self):
        Turn.remove(self)
        Group.remove(self)
        Turn.update = self.backup

    def input(self, action, target):
        vec_x = Camera.target.x / Global.BLOCK + target.x
        vec_y = Camera.target.y / Global.BLOCK + target.y
        if action == 'idle':
            self.tool.input(0, self.location.get_tile(vec_x, vec_y))
            self.tool.last = None
        elif action == 'switch':
            self.tool.cancel()
        elif action == 'use':
            self.tool.input(1, self.location.get_tile(vec_x, vec_y))
        elif action == 'delete':
            self.tool.input(2, self.location.get_tile(vec_x, vec_y))
        elif action == 'prev':
            if action != self.prev_command:
                self.display_text = self.tool.cycle(-1)
        elif action == 'next':
            if action != self.prev_command:
                self.display_text = self.tool.cycle(1)
        elif action == 'up':
            Camera.target.load(Camera.target.x, Camera.target.y - Editor.scroll)
        elif action == 'down':
            Camera.target.load(Camera.target.x, Camera.target.y + Editor.scroll)
        elif action == 'left':
            Camera.target.load(Camera.target.x - Editor.scroll, Camera.target.y)
        elif action == 'right':
            Camera.target.load(Camera.target.x + Editor.scroll, Camera.target.y)
        elif action == 'tiles':
            self.tool.cancel()
            self.tool = ToolTerrain(self.location)
            self.display_text = 'Terrain Tool'
        elif action == 'props':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Props Tool'
        elif action == 'items':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Items Tool'
        elif action == 'units':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Units Tool'
        elif action == 'weapons':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Weapons Tool'
        elif action == 'armors':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Armors Tool'
        elif action == 'headgears':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Headgears Tool'
        elif action == 'others':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Others Tool'
        elif action == 'save':
            self.tool.cancel()
            self.location.turn()
            self.display_text = 'saved'
        elif action == 'quit':
            pygame.quit()
            sys.exit()
        self.prev_command = action
        return 0

    def draw(self, surface):
        if self.display_text:
            surface.blit(self.font.render(self.display_text, 1, (0, 0, 0)), (16, 16))


class ToolTerrain:
    def __init__(self, loc):
        self.tile_list = Data.get_cache('tiles')
        self.text = 'dirt'
        self.location = loc
        self.tile = loc.get_tile(0, 0)
        self.prev_tile = loc.get_tile(0, 0).terrain
        self.current = 0
        self.last = None  # unused

    def cancel(self):
        self.tile.terrain = self.prev_tile

    def cycle(self, inc):
        self.current += inc
        if self.current >= self.tile_list.__len__():
            self.current = 0
        if self.current < 0:
            self.current = self.tile_list.__len__() - 1
        self.text = self.tile_list[self.current][0]
        return self.text

    def enter(self, text):
        self.text = text

    def input(self, button, tile):
        text = self.text
        if not button:
            self.cancel()
        elif button != 1:
            self.tile.set_terrain('')
        self.tile = tile
        self.prev_tile = tile.terrain
        self.tile.set_terrain(text)
        self.update(self.tile.x, self.tile.y)

    def is_terrain(self, x, y, terrain):
        r = self.location.get_tile(self.tile.x + x, self.tile.y + y).terrain
        if r:
            return 1 if r.name.split(' ')[0] == terrain else 0
        return 0

    def update(self, x, y):
        tile = self.location.get_tile(x, y)
        if tile.terrain:
            name_type = tile.terrain.name.split(' ')[0]
            if name_type in ['dirt']:
                grid = [self.is_terrain(0, -1, name_type), self.is_terrain(-1, 0, name_type),
                        self.is_terrain(1, 0, name_type), self.is_terrain(0, 1, name_type)]
                if grid in [[1, 1, 1, 1], [1, 1, 0, 1], [1, 0, 1, 1]]:
                    tile.set_terrain(name_type)
                if grid in [[0, 1, 1, 1], [0, 1, 1, 0]]:
                    tile.set_terrain(name_type + ' top')
                if grid in [[0, 1, 0, 1]]:
                    tile.set_terrain(name_type + ' left')
                if grid in [[0, 0, 1, 1]]:
                    tile.set_terrain(name_type + ' right')
                if grid in [[0, 1, 0, 0]]:
                    tile.set_terrain(name_type + ' edge left')
                if grid in [[0, 0, 1, 0]]:
                    tile.set_terrain(name_type + ' edge right')
                if grid in [[1, 1, 0, 0]]:
                    tile.set_terrain(name_type + ' corner left')
                if grid in [[1, 0, 1, 0]]:
                    tile.set_terrain(name_type + ' corner right')


class ToolObject:
    def __init__(self, loc, object_type):
        self.location = loc
        self.text = 'Crate'
        self.selection = Stock.get('Crate').add()
        self.tile = loc.get_tile(0, 0)
        self.object_list = list(Data.get_cache(object_type))
        self.current = 0
        self.last = None

    def cancel(self):
        self.selection.remove()

    def cycle(self, inc):
        self.current += inc
        if self.current >= self.object_list.__len__():
            self.current = 0
        if self.current < 0:
            self.current = self.object_list.__len__() - 1
        self.text = self.object_list[self.current][0]
        self.selection.remove()
        self.selection = Stock.get(self.text.title()).add()
        return self.text

    def input(self, button, tile):
        if not button:
            self.selection.relocate(tile.x, tile.y)
        elif button == 1:
            self.selection.relocate(tile.x, tile.y, force=1)
            preexisting = 0
            for i in tile.things:
                if i != self.selection and i.name == self.text:
                    preexisting = 1
                    break
            if not preexisting:
                self.selection = Stock.get(self.text.title()).add()
                self.selection.relocate(tile.x, tile.y, force=1)
        else:
            if self.last != tile:
                if tile.things:
                    for i in reversed(tile.things):
                        if i != self.selection:
                            i.remove()
                            break
                self.last = tile
