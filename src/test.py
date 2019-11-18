from time import time
import pyglet

from pyglet.gl import *


class MainTest:
    def __init__(self):
        self.window = pyglet.window.Window(
            width=800, height=600,
            fullscreen=False,
            vsync=False,
            resizable=True
        )
        pyglet.resource.path = ['../data']
        pyglet.resource.reindex()
        self.frame = 0, time()
        self.init_window()

    def init_window(self):
        def loop(dt):
            pass

        def on_draw():
            if time() - self.frame[1] > 1:
                print('fps:', self.frame[0])
                self.frame = 0, time()
            else:
                self.frame = self.frame[0] + 1, self.frame[1]
            self.window.clear()

        self.window.on_draw = on_draw
        dt = 1/60.0
        pyglet.clock.schedule_interval(loop, dt)
        pyglet.app.run()


if __name__ == '__main__':
    MainTest()
