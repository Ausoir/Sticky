import sys

import pygame

from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn


class Editor:
    scroll = 160

    def __init__(self, loc):
        Turn.queue.append(self)
        Group.interface.append(self)
        Group.gui.append(self)
        self.location = loc
        self.font = pygame.font.SysFont('Helvetica', 20)
        self.visible = 1
        self.delay = 0
        self.mouse = [0, 0]
        self.tool = ToolTerrain(self.location)
        self.display_text = ''
        self.enter = 0
        self.button = 0

    def input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.mouse = pygame.mouse.get_pos()
            self.mouse = Global.get_relative_tile_pos(self.mouse[0], self.mouse[1], Camera.pos[0], Camera.pos[1])
            self.tool.mouse_move(self.button, self.location.get_tile(self.mouse[0], self.mouse[1]))
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.button = event.button
            self.tool.mouse_down(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.button = 0
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            if event.key == pygame.K_F4:
                self.tool.cancel()
                self.location.turn()
            elif event.key == 49:
                self.tool.cancel()
                self.tool = ToolTerrain(self.location)
            elif event.key == 50:
                self.tool.cancel()
                self.tool = ToolObject(self.location)
            elif event.key == pygame.K_RETURN:
                if self.enter:
                    self.enter = 0
                    self.tool.enter(self.display_text)
                    self.display_text = ''
                else:
                    self.enter = 1
            elif event.key == pygame.K_BACKSPACE:
                self.display_text = self.display_text[:len(self.display_text)-1]
            elif self.enter:
                self.display_text += chr(event.key)
            elif not self.enter:
                if event.key == pygame.K_w:
                    Camera.target = [Camera.target[0], Camera.target[1] - Editor.scroll]
                elif event.key == pygame.K_s:
                    Camera.target = [Camera.target[0], Camera.target[1] + Editor.scroll]
                elif event.key == pygame.K_a:
                    Camera.target = [Camera.target[0] - Editor.scroll, Camera.target[1]]
                elif event.key == pygame.K_d:
                    Camera.target = [Camera.target[0] + Editor.scroll, Camera.target[1]]
        return 0

    def draw(self, surface):
        if self.display_text:
            surface.blit(self.font.render(self.display_text, 1, (0, 0, 0)), (16, 16))

    def turn(self):
        self.delay = 4
        self.display_text = ''


class ToolTerrain:
    def __init__(self, loc):
        self.text = ''
        self.tile = loc.get_tile(0, 0)
        self.prev_tile = None

    def cancel(self):
        self.tile.terrain = self.prev_tile

    def enter(self, text):
        self.text = text

    def mouse_move(self, button, tile):
        text = self.text
        if not button:
            self.cancel()
        elif button == 3:
            text = ''
        self.tile = tile
        self.prev_tile = tile.terrain
        self.tile.set_terrain(text)

    def mouse_down(self, button):
        self.tile.set_terrain(self.text)
        self.prev_tile = self.tile.terrain


class ToolObject:
    def __init__(self, loc):
        self.location = loc
        self.text = 'crate'
        self.selection = Stock.get('crate', self.location).add()
        self.tile = loc.get_tile(0, 0)
        self.prev_tile = None

    def cancel(self):
        self.selection.remove()

    def enter(self, text):
        self.text = text
        self.cancel()
        self.mouse_down(1)

    def mouse_move(self, button, tile):
        if not button:
            self.selection.relocate(tile.x, tile.y)
        elif button == 1:
            if not tile.things:
                self.mouse_down(1)
                self.selection.relocate(tile.x, tile.y)
        elif button == 3:
            if tile.things:
                for i in tile.things:
                    i.remove()
                self.mouse_down(1)

    def mouse_down(self, button):
        self.selection = Stock.get(self.text, self.location).add()
        if not self.selection:
            self.selection = Stock.get('crate', self.location).add()
