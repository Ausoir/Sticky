import pyglet


class Execute:
    def __init__(self):
        self.window = pyglet.window.Window(
            width=1000, height=600,
            fullscreen=False,
            vsync=False,
            resizable=True
        )
        self.window.set_minimum_size(320, 200)
        self.window.set_location(320, 40)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.resource.path = ['../data']
        pyglet.resource.reindex()
        self.init_window()

    def init_window(self):
        def loop(dt):
            pass

        def on_draw():
            self.window.clear()
            fps_display.draw()

        self.window.on_draw = on_draw
        fps_display = pyglet.window.FPSDisplay(window=self.window)
        pyglet.clock.schedule_interval(loop, 1/40.0)
        pyglet.app.run()


if __name__ == '__main__':
    Execute()
