import pyglet
from pyglet.gl import *

from src.game import Global
from src.tools.Space import Space
from src.game.Camera import Camera
from src.map.MapView import MapView
from src.game.Game import Game
from src.game.DrawGroup import DrawGroup
from src.game.Turn import Turn
from src.interface.Textbox import Textbox
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Random import Random


# noinspection PyAbstractClass
class Execute(pyglet.window.Window):
    def __init__(self):
        self.setting = Dialog.to_dict(Data.process_raw(Data.read('data/setting.txt')))
        super(Execute, self).__init__(self.setting['width'], self.setting['height'], ' ',
                                      fullscreen=self.setting['fullscreen'] == 1, vsync=False, resizable=True)
        self.dt = 0
        self.fps = 1 / 36.0
        self.set_location(self.setting['x'], self.setting['y'])
        self.init_other()
        self.monologue = Textbox(40, 40)
        glEnable(pyglet.gl.GL_BLEND)
        glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(Global.mask_color[0], Global.mask_color[1], Global.mask_color[2], Global.mask_color[3])

    def init_other(self):
        Global.r = Random()
        Global.r_t = Random()
        Space.reusable = Space()
        from src.entity.Stock import Stock
        from src.interface.MenuAll import MenuAll
        from src.map.Tile import Tile
        Data.init()
        Turn.init()
        Tile.init(Data.process_raw(Data.read('data/raw/tiles.txt')))
        Dialog.init()
        Stock.init()
        Global.draw_group = DrawGroup()
        pyglet.font.add_file(Data.direct('data/Ubuntu-Regular.ttf'))
        Global.font = pyglet.font.load('Default Font', 18)
        Global.main = self
        Global.blank_form = Data.get_form('none')
        Global.map_view = MapView()
        Global.menu = MenuAll()
        Global.player = Game()

    def set_fullscreen(self, fullscreen=True, screen=None, mode=None,
                       width=None, height=None):
        super().set_fullscreen(fullscreen, width=Global.main.setting['res_x'], height=Global.main.setting['res_y'])
        self.set_location(0, 0)
        self.clear()

    def on_text(self, text):
        Global.player.control.on_text(text)

    def on_key_press(self, symbol, modifiers):
        Global.player.control.input(symbol)

    def on_key_release(self, symbol, modifiers):
        Global.player.control.input(-symbol)

    def on_mouse_press(self, x, y, button, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.turn()
        Global.player.control.target_mark.form.show(False)
        Global.player.control.move_mark(Global.player.control.cursor_tile)
        Global.player.control.input(button)

    def on_mouse_release(self, x, y, button, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.input(-button)

    def on_mouse_motion(self, x, y, dx, dy):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        Global.player.control.cursor = [x, Global.DISPLAY[1] - y]
        Global.player.control.input(0)

    def on_move(self, x, y):
        self.setting['x'] = x
        self.setting['y'] = y

    def on_resize(self, width, height):
        self.setting['width'] = width
        self.setting['height'] = height
        Global.DISPLAY = (int(width / 2) * 2, int(height / 2) * 2)
        Global.CENTER = (int(Global.DISPLAY[0] / 2), int(Global.DISPLAY[1] / 2))
        Global.SCREEN_TILES = (int(Global.DISPLAY[0] / Global.BLOCK), int(Global.DISPLAY[1] / Global.BLOCK))
        glViewport(0, 0, Global.DISPLAY[0], Global.DISPLAY[1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        horizontal = int(Global.DISPLAY[0] / 2)
        vertical = int(Global.DISPLAY[1] / 2)
        glOrtho(-horizontal, horizontal, -vertical, vertical, -1000, 4)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glTranslatef(Global.CURRENT_OFFSET[0] - Global.OFFSET[0], Global.CURRENT_OFFSET[1] - Global.OFFSET[1], 0)
        Global.CURRENT_OFFSET = Global.OFFSET
        Global.player.set_darkness()
        self.monologue.on_resize()

    def on_activate(self):
        Global.player.control.clear_press()

    def on_close(self):
        self.setting['fullscreen'] = 1 if self.fullscreen else 0
        result = Dialog.dict(self.setting)
        Data.write('data/setting.txt', result.replace(',', '\n').replace(':', ',')[1:][:-1])
        self.close()

    def loop(self, dt):
        self.dt += dt
        if self.dt > self.fps:
            self.dt = 0
            Camera.update()
            Turn.update()
            self.monologue.update()
        pyglet.clock.schedule_once(self.loop, self.fps - self.dt)

    def on_draw(self):
        self.clear()
        Global.draw_group.draw()
        Global.menu.draw()
        Global.player.draw()

    def quit(self):
        Global.player.control.output('quit')
        Global.player.world.save()
        Global.player.save()
        self.on_close()


if __name__ == '__main__':
    main = Execute()
    main.loop(999)
    pyglet.app.run()
