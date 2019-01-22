from src.form.Sprite import Sprite


# Has form, has tile position
from src.game.Turn import Turn
from src.map.Tile import Tile


class Object:
    BLOCK = 40

    def __init__(self, form, map):
        Turn.queue.append(self)
        self.id = -1
        self.seed = -1
        self.form = None
        self.make_form(form)
        self.map = map
        self.pos = map.get_tile(4, 4)
        self.move(0, 0)
        self.animation_move_from = [0, 0]
        self.delay = 0

    def load(self, p):
        self.id = p[0]
        self.seed = p[1]
        self.pos.load(p[2])
        return 3

    def make_form(self, arg):
        self.form = Sprite(texture_name=arg)

    def draw(self, surface, pos):
        self.animation_move_from[0] += (pos[0] - self.animation_move_from[0]) * .1
        y = pos[1] - self.animation_move_from[1]
        if y > 0:
            self.animation_move_from[1] += min(16, y)
        else:
            self.animation_move_from[1] += y * .1
        self.form.draw(surface, self.animation_move_from)

    def turn(self):
        if self.move(0, 8, Tile.CHECK_ANY):
            self.on_fall()

    def move(self, x, y, flag=Tile.CHECK_NONE):
        old_pos = self.pos
        self.pos = self.map.collide_line(self.pos, x, y, flag)
        if self.pos != old_pos:
            old_pos.remove(self)
            self.pos.things.append(self)
            return 1
        return 0

    def on_fall(self):
        pass
