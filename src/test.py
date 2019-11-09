import os
import sys

import pygame
import pyglet

from pyglet.gl import *
from src.game import Global


class MainTest:
    def __init__(self, window):
        self.window = window

    def init_window(self):
        def on_key_press(symbol, modifiers):
            key = pyglet.window.key
            if symbol == key.ESCAPE:
                sys.exit()
            if symbol == pygame.QUIT:
                Global.player.control.quit()
            # elif symbol == pygame.VIDEORESIZE:
            #     self.resize(event.w, event.h)
            Global.player.control.input(symbol)

        def on_mouse_press(x, y, button, modifiers):
            Global.player.control.input(x, y, button)

        def loop(dt):
            pass

        def on_draw():
            window.clear()
            glClear(GL_COLOR_BUFFER_BIT)
            glLoadIdentity()
            glBegin(GL_TRIANGLES)
            glVertex2f(0, 0)
            glVertex2f(window.width, 0)
            glVertex2f(window.width, window.height)
            glEnd()
            image = pyglet.resource.image("Error.png")
            image.blit(0, 0)

        print('start')
        self.window.push_handlers(on_key_press)
        self.window.push_handlers(on_mouse_press)
        self.window.on_draw = on_draw
        pyglet.clock.schedule(loop)
        pyglet.app.run()


if __name__ == '__main__':
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (120, 80)
    pyglet.resource.path = ['..\\data']
    pyglet.resource.reindex()
    window = pyglet.window.Window(
        fullscreen=False,
        vsync=False,
        resizable=True
    )
    Global.main = MainTest(window)
    Global.main.init_window()
