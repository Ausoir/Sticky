from time import time
import pyglet

from pyglet.gl import *
from pyglet import font

from src.game import Global
from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.MapView import MapView
from src.game.Player import Player
from src.game.DrawGroup import DrawGroup
from src.game.Turn import Turn
from src.tools.Random import Random


class Execute:
    def __init__(self):
        self.window = pyglet.window.Window(
            width=800, height=600,
            fullscreen=False,
            vsync=False,
            resizable=True
        )
        self.window.set_minimum_size(320, 200)
        self.window.set_location(120, 80)
        pyglet.gl.glClearColor(0, 0, 0, 1)
        pyglet.resource.path = ['../data']
        pyglet.resource.reindex()
        self.frame = 0, time()
        self.init_other()
        self.init_window()

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
        font.add_file(Data.direct('Ubuntu-Regular.ttf'))
        Global.font = font.load('Default Font', 20)
        Global.main = self
        Global.draw_group = DrawGroup()
        Global.blank_form = Data.get_form('g_0x0')
        Global.map_view = MapView()
        Global.player = Player()

    def init_window(self):
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                Global.player.control.quit()
            elif symbol == pyglet.window.key.F:
                Global.draw_group.scene.scale += .3
            elif symbol == pyglet.window.key.G:
                Global.draw_group.scene.scale -= .3
            Global.player.control.input(symbol)

        def on_key_release(symbol, modifiers):
            Global.player.control.input(-symbol)

        def on_mouse_press(x, y, button, modifiers):
            Global.player.control.mouse = [x, y]
            Global.player.control.input(button)

        def on_mouse_release(x, y, button, modifiers):
            Global.player.control.mouse = [x, y]
            Global.player.control.input(-button)

        def on_mouse_motion(x, y, dx, dy):
            Global.player.control.mouse = [x, y]
            Global.player.control.input(0)

        def on_resize(width, height):
            Global.DISPLAY = (width, height)
            Global.CENTER = (Global.DISPLAY[0] / 2, Global.DISPLAY[1] / 2)
            Global.SCREEN_TILES = (int(Global.DISPLAY[0] / Global.BLOCK), int(Global.DISPLAY[1] / Global.BLOCK))
            Global.draw_group.on_resize()
            Global.map_view.on_resize()

        def loop(dt):
            Camera.update()
            Turn.update()
            Global.map_view.update()

        def on_draw():
            if time() - self.frame[1] > 1:
                print('fps:', self.frame[0])
                self.frame = 0, time()
            else:
                self.frame = self.frame[0] + 1, self.frame[1]
            self.window.clear()
            Global.draw_group.draw()

        self.window.push_handlers(on_key_press)
        self.window.push_handlers(on_key_release)
        self.window.push_handlers(on_mouse_press)
        self.window.push_handlers(on_mouse_release)
        self.window.push_handlers(on_mouse_motion)
        self.window.push_handlers(on_resize)
        self.window.on_draw = on_draw
        dt = 1/60.0
        pyglet.clock.schedule_interval(loop, dt)
        pyglet.app.run()
        on_resize(self.window.width, self.window.height)


if __name__ == '__main__':
    Execute()
