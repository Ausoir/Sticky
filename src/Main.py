import sys

import pygame

from src.entity.Unit import Unit
from src.game.Group import Group
from src.game.Turn import Turn
from src.interface.Control import Control
from src.interface.Menu import Menu
from src.map.Map import Map
from src.tools.Data import Data
from src.tools.Math import Math


class Main:
    def __init__(self):
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.display = (1200, 600)
        self.screen = pygame.display.set_mode(self.display, pygame.RESIZABLE, 32)
        Math.init()
        Data.init()
        pygame.display.set_icon(Data.get_image('Icon_1x0', 1))
        pygame.display.set_caption('Sticky', 'Sticky')

        self.map = Map(40, 12)
        self.player = Unit('unit/Man', self.map)
        self.another = Unit('unit/Man', self.map)
        control = Control(Menu(), self.player)
        Group.interface.append(control)
        self.loop()

    def loop(self):
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    display = (event.w, event.h)
                    Main.screen = pygame.display.set_mode(display, pygame.RESIZABLE, 32)
                Group.interface.input(event)
            self.draw()
            Turn.update()

    def draw(self):
        Group.update()
        self.screen.fill((255, 255, 255))
        Group.background.draw(self.screen)
        self.map.draw(self.screen)
        self.map.draw_objects(self.screen)
        Group.gui.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    Main()
