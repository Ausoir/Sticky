import os
import sys

import pygame

from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Player import Player
from src.game.Turn import Turn
from src.interface.Textbox import Textbox


class Main:
    def __init__(self):
        from src.tools.Random import Random
        from src.tools.Math import Math
        from src.tools.Data import Data
        from src.entity.Stock import Stock
        from src.map.Tile import Tile
        from src.entity.Space import Space
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(Global.DISPLAY, pygame.DOUBLEBUF, 16)
        self.overlay = pygame.Surface((Global.BLOCK, Global.BLOCK), pygame.SRCALPHA, 16)
        self.overlay = self.overlay.convert_alpha(self.overlay)
        self.colors = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.fade = 0
        Math.init()
        Global.r = Random()  # todo: set to constant on production
        Space.reusable = Space()
        Data.init()
        Stock.init()
        Tile.init()
        Global.font = pygame.font.Font(Data.direct('data/Ubuntu-Regular.ttf'), 20)
        pygame.display.set_icon(Data.get_cache('icon_1x0')[1])
        pygame.display.set_caption('Sticky', 'Sticky')
        self.textbox = Textbox(self, 16, Global.DISPLAY[1] - 48)
        self.text_mode = False

        self.on_pause = None
        self.pause = 0
        self.resize(Global.DISPLAY[0], Global.DISPLAY[1])

    def colorize(self, index, color, fade=0):
        if index == 0:
            self.fade = fade
        self.colors[index] = color
        self.overlay.fill((0, 0, 0, 0))
        for layer in self.colors:
            self.overlay.fill(layer, special_flags=pygame.BLEND_RGBA_MAX)

    def resize(self, width, height):
        Global.DISPLAY = (width, height)
        Global.CENTER = (Global.DISPLAY[0] / 2, Global.DISPLAY[1] / 2)
        Global.SCREEN_TILES = (int(Global.DISPLAY[0] / Global.BLOCK), int(Global.DISPLAY[1] / Global.BLOCK))
        if Global.player:
            Global.player.background.resize(Global.DISPLAY)
            Global.player.location.resize()
        Main.screen = pygame.display.set_mode(Global.DISPLAY, pygame.RESIZABLE, 16)

    def loop(self):
        dt = 0
        fps = 60
        frame = 0
        last = 0
        while not self.pause:
            self.clock.tick(fps + dt)
            dt = self.clock.get_time()
            frame += 1
            if frame > 100:
                print(str(int(pygame.time.get_ticks() - last)/100))
                last = pygame.time.get_ticks()
                frame = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Global.player.control.quit()
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event.w, event.h)
                if self.text_mode:
                    self.textbox.input(event)
                else:
                    Global.player.control.input(event)
            self.draw()
            Turn.update()
        if self.on_pause:
            self.on_pause()

    def draw(self):
        Camera.update()
        Group.update()
        self.screen.fill((0, 0, 0))
        Global.player.location.draw(self.screen)
        Group.effects.draw(self.screen)
        Global.player.monologue.draw(self.screen)
        Global.menu.draw(self.screen)
        if self.fade > 0:
            color = self.colors[0]
            self.colorize(0, [color[0], color[1], color[2], color[3]], self.fade)
            self.colors[0][3] = max(0, self.colors[0][3] - self.fade)
        self.textbox.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (120, 80)
    Global.main = Main()
    Global.player = Player()
    for i in sys.argv[1:]:
        if i == 'editor':
            Global.player.switch()
    Global.main.loop()
