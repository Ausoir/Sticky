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

        Turn.update = update
        Group.gui.append(self)
        control.set_keymap('data/editor_keymap.txt')
        control.player = self
        self.location = loc
        self.font = pygame.font.SysFont('Helvetica', 20)
        self.visible = 1
        self.mouse = [0, 0]
        self.tool = ToolTerrain(self.location)
        self.display_text = ''
        self.enter = 0

    def remove(self):
        Turn.remove(self)
        Group.remove(self)

    def input(self, action, target):
        vec_x = Camera.target[0] / Global.BLOCK + target[0]
        vec_y = Camera.target[1] / Global.BLOCK + target[1] - 1
        if action == 'idle':
            self.tool.input(0, self.location.get_tile(vec_x, vec_y))
        elif action == 'switch':
            Global.main.world.switch()
        elif action == 'use':
            self.tool.input(1, self.location.get_tile(vec_x, vec_y))
        elif action == 'delete':
            self.tool.input(2, self.location.get_tile(vec_x, vec_y))
        elif action == 'prev':
            self.display_text = self.tool.cycle(-1)
        elif action == 'next':
            self.display_text = self.tool.cycle(1)
        elif action == 'up':
            Camera.target = [Camera.target[0], Camera.target[1] - Editor.scroll]
        elif action == 'down':
            Camera.target = [Camera.target[0], Camera.target[1] + Editor.scroll]
        elif action == 'left':
            Camera.target = [Camera.target[0] - Editor.scroll, Camera.target[1]]
        elif action == 'right':
            Camera.target = [Camera.target[0] + Editor.scroll, Camera.target[1]]
        elif action == 'tiles':
            self.tool.cancel()
            self.tool = ToolTerrain(self.location)
            self.display_text = 'Terrain Tool'
        elif action == 'props':
            self.tool.cancel()
            self.tool = ToolObject(self.location, action)
            self.display_text = 'Props Tool'
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
        elif action == 'save':
            self.location.turn()
            self.display_text = 'saved'
        elif action == 'quit':
            pygame.quit()
            sys.exit()
        return 0

    def draw(self, surface):
        if self.display_text:
            surface.blit(self.font.render(self.display_text, 1, (0, 0, 0)), (16, 16))


class ToolTerrain:
    def __init__(self, loc):
        self.tile_list = Data.process_raw(Data.get_cache_file('raw/tile.txt'))
        self.text = 'dirt'
        self.tile = loc.get_tile(0, 0)
        self.prev_tile = None
        self.current = 0

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
            text = ''
        self.tile = tile
        self.prev_tile = tile.terrain
        self.tile.set_terrain(text)


class ToolObject:
    def __init__(self, loc, object_type):
        self.location = loc
        self.text = 'Crate'
        self.selection = Stock.get('Crate', self.location).add()
        self.tile = loc.get_tile(0, 0)
        self.prev_tile = None
        self.object_list = Data.process_raw(Data.get_cache_file('raw/'+object_type+'.txt'))
        self.current = 0

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
        self.selection = Stock.get(self.text.title(), self.location)
        return self.text

    def input(self, button, tile):
        if not button:
            self.selection.relocate(tile.x, tile.y)
        elif button == 1:
            if not tile.things:
                self.selection = Stock.get(self.text.title(), self.location).add()
                self.selection.relocate(tile.x, tile.y)
        else:
            if tile.things:
                for i in tile.things:
                    i.remove()
