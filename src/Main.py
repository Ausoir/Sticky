import sys

import pygame

from src.game import Global
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn


class Main:
    def __init__(self):
        from src.tools.Random import Random
        from src.tools.Math import Math
        from src.tools.Data import Data
        from src.entity.Stock import Stock
        from src.game.World import World
        pygame.font.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(Global.DISPLAY, pygame.RESIZABLE, 32)
        Math.init()
        Random.init(99999)
        Data.init()
        Stock.init()
        pygame.display.set_icon(Data.get_cache('icon_1x0')[1])
        pygame.display.set_caption('Sticky', 'Sticky')

        self.world = World()

        self.on_pause = None
        self.pause = 0
        for i in sys.argv[1:]:
            if i == 'editor':
                self.world.switch()

    def loop(self):
        dt = 0
        fps = 60
        while not self.pause:
            self.clock.tick(fps + dt)
            dt = self.clock.get_time()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.VIDEORESIZE:
                    Global.DISPLAY = (event.w, event.h)
                    Main.screen = pygame.display.set_mode(Global.DISPLAY, pygame.RESIZABLE, 32)
                self.world.control.input(event)
            self.draw()
            Turn.update()
        if self.on_pause:
            self.on_pause()

    def draw(self):
        Camera.update()
        Group.update()
        self.screen.fill((220, 250, 250))
        self.world.map.draw(self.screen)
        Group.objects.draw(self.screen)
        Group.effects.draw(self.screen)
        self.world.control.menu.draw(self.screen)
        pygame.display.flip()


if __name__ == '__main__':
    Global.main = Main()
    Global.main.loop()
