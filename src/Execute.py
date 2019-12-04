import pyglet

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
            width=1000, height=600,
            fullscreen=False,
            vsync=False,
            resizable=True
        )
        self.window.set_minimum_size(320, 200)
        self.window.set_location(120, 80)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glClearColor(0, 0, 0, 1)
        pyglet.resource.path = ['../data']
        pyglet.resource.reindex()
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
        Global.font = font.load('Default Font', 18)
        Global.main = self
        Global.draw_group = DrawGroup()
        Global.blank_form = Data.get_form('none')
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
            Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
            Global.player.control.input(button)

        def on_mouse_release(x, y, button, modifiers):
            Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
            Global.player.control.input(-button)

        def on_mouse_motion(x, y, dx, dy):
            Global.player.control.cursor = [x, Global.DISPLAY[1] - y]

        def on_resize(width, height):
            Global.DISPLAY = (width, height)
            Global.CENTER = (Global.DISPLAY[0] / 2, Global.DISPLAY[1] / 2)
            Global.SCREEN_TILES = (int(Global.DISPLAY[0] / Global.BLOCK), int(Global.DISPLAY[1] / Global.BLOCK))

        def loop(dt):
            Camera.update()
            Turn.update()
            Global.map_view.update()

        def on_draw():
            self.window.clear()
            Global.draw_group.draw()
            Global.menu.draw()
            fps_display.draw()

        self.window.push_handlers(on_key_press)
        self.window.push_handlers(on_key_release)
        self.window.push_handlers(on_mouse_press)
        self.window.push_handlers(on_mouse_release)
        self.window.push_handlers(on_mouse_motion)
        self.window.push_handlers(on_resize)
        self.window.on_draw = on_draw
        fps_display = pyglet.window.FPSDisplay(window=self.window)
        pyglet.clock.schedule_interval(loop, 1/40.0)
        pyglet.app.run()
        on_resize(self.window.width, self.window.height)


if __name__ == '__main__':
    Execute()
