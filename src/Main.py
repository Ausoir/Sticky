import pygame
import sys
from src.entity.Unit import Unit

clock = pygame.time.Clock()
display = (1200, 600)
screen = pygame.display.set_mode(display, 0, 32)
surface = pygame.Surface(screen.get_size())
surface = surface.convert()

def loop():
    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_LEFT:
                    sprite.pos[0] += 10
                elif event.key == pygame.K_RIGHT:
                    sprite.pos[0] -= 10
                elif event.key == pygame.K_UP:
                    sprite.pos[1] += 10
                elif event.key == pygame.K_DOWN:
                    sprite.pos[1] -= 10
        draw()


def draw():
    surface.fill((255, 255, 255))
    screen.blit(surface, (0, 0))
    sprite.draw(screen)
    pygame.display.flip()
    pygame.display.update()


sprite = Unit('unit/Man')
sprite.load([-1, [100, 40], [20, 20]])
loop()
