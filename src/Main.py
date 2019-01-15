import sys

import pygame

from src.Group import Group
from src.entity.Object import Object
from src.entity.Unit import Unit
from src.interface.Menu import Menu
from src.other.Data import Data
from src.interface.Control import Control

pygame.font.init()
clock = pygame.time.Clock()
display = (1200, 600)
screen = pygame.display.set_mode(display, 0, 32)
Data.init()
Menu.init()


def loop():
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            Group.interface.input(event)
        draw()


def draw():
    obj.update()
    screen.fill((255, 255, 255))
    Group.draw(screen)
    pygame.display.flip()


Group.interface.append(Control())
test = Object('Man_skin_1x0')
test.form.pivot.load(test.form.size.x / 2, 0)
test.load([-1, -1, [500, 200]])
obj = Unit('unit/Man')
obj.load([-1, -1, [200, 200]])
loop()
