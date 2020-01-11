import pyglet
from pyglet.gl import *

from time import time
from src.game import Global
from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.MapView import MapView
from src.player.Player import Player
from src.game.DrawGroup import DrawGroup
from src.game.Turn import Turn
from src.interface.Textbox import Textbox
from src.tools.Random import Random


# noinspection PyAbstractClass
class Execute(pyglet.window.Window):
    def __init__(self, width, height, title=''):
        super(Execute, self).__init__(width, height, title, fullscreen=False, vsync=False, resizable=True)
        self.fps = 1 / 40.0
        self.frame_rate = 0, time()
        self.set_minimum_size(320, 200)
        self.set_location(320, 40)
        pyglet.resource.path = ['../data']
        pyglet.resource.reindex()
        self.monologue = Textbox(40, 40)
        self.init_other()
        glEnable(pyglet.gl.GL_BLEND)
        glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(Global.mask_color[0], Global.mask_color[1], Global.mask_color[2], Global.mask_color[3])

    def init_other(self):
        Global.r = Random()  # todo: set to constant on production
        Space.reusable = Space()
        from src.tools.Data import Data
        from src.entity.Stock import Stock
        from src.map.Tile import Tile
        Data.init()
        Stock.init()
        Tile.init()
        Turn.init()
        pyglet.font.add_file(Data.direct('Ubuntu-Regular.ttf'))
        Global.font = pyglet.font.load('Default Font', 18)
        Global.main = self
        Global.draw_group = DrawGroup()
        Global.blank_form = Data.get_form('none')
        Global.map_view = MapView()
        Global.player = Player()

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            Global.player.control.quit()
        Global.player.control.input(symbol)

    def on_key_release(self, symbol, modifiers):
        Global.player.control.input(-symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.input(button)

    def on_mouse_release(self, x, y, button, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.input(-button)

    def on_mouse_motion(self, x, y, dx, dy):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.input(0)

    def on_resize(self, width, height):
        Global.DISPLAY = (int(width / 2) * 2, int(height / 2) * 2)
        Global.CENTER = (int(Global.DISPLAY[0] / 2), int(Global.DISPLAY[1] / 2))
        Global.SCREEN_TILES = (int(Global.DISPLAY[0] / Global.BLOCK), int(Global.DISPLAY[1] / Global.BLOCK))
        self.monologue.x = Global.CENTER[0]
        Global.player.on_resize()

        glViewport(0, 0, Global.DISPLAY[0], Global.DISPLAY[1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        horizontal = int(Global.DISPLAY[0] / 2)
        vertical = int(Global.DISPLAY[1] / 2)
        glOrtho(-horizontal, horizontal, -vertical, vertical, -1000, 4)
        glTranslatef(-Global.CENTER[0], -Global.CENTER[1], 0)

    def on_text(self, text):
        Global.player.control.on_text(text)

    def on_activate(self):
        Global.player.control.clear_press()

    def loop(self, dt):
        if time() - self.frame_rate[1] > self.fps:
            self.frame_rate = 0, time()
            Camera.update()
            Turn.update()
            Global.map_view.update()
        else:
            self.frame_rate = self.frame_rate[0] + 1, self.frame_rate[1]

    def on_draw(self):
        self.clear()
        Global.draw_group.draw()
        Global.menu.draw()
        Global.player.draw()
        self.monologue.draw()
        self.batch.draw()


if __name__ == '__main__':
    main = Execute(800, 600, 'Stuff')
    pyglet.clock.schedule_interval(main.loop, 1 / 100.0)
    pyglet.app.run()
