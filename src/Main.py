import sys

import pygame

from src.Editor import Editor
from src.entity.Stock import Stock
from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn
from src.game.World import World
from src.tools.Data import Data
from src.tools.Math import Math
from src.tools.Random import Random


class Main:
    def __init__(self):
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(Global.DISPLAY, pygame.RESIZABLE, 32)
        Math.init()
        Random.init(99999)
        Data.init()
        Stock.init()
        pygame.display.set_icon(Data.get_image('Icon_1x0', 1))
        pygame.display.set_caption('Sticky', 'Sticky')

        self.world = World()

        self.on_pause = None
        self.pause = 0
        for i in sys.argv[1:]:
            if i == 'editor':
                self.world.switch()

    def loop(self):
        while not self.pause:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    Global.DISPLAY = (event.w, event.h)
                    Main.screen = pygame.display.set_mode(Global.DISPLAY, pygame.RESIZABLE, 32)
                Group.interface.input(event)
            self.draw()
            Turn.update()
        if self.on_pause:
            self.on_pause()

    def draw(self):
        Camera.update()
        Group.update()
        self.screen.fill((255, 255, 255))
        Group.background.draw(self.screen)
        self.world.map.draw(self.screen)
        self.world.map.draw_objects(self.screen)
        Group.effects.draw(self.screen)
        Group.gui.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    Global.main = Main()
    Global.main.loop()
