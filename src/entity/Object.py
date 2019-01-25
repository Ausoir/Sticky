from src.form.Sprite import Sprite


# Has form, has tile position
from src.game.Turn import Turn
from src.map.Tile import Tile


class Object:
    BLOCK = 40

    def __init__(self, form, loc):
        Turn.queue.append(self)
        self.id = 0
        self.name = 'none'
        self.seed = 0
        self.form = None
        self.make_form(form)
        self.location = loc
        self.location.record.append(self)
        self.save = 1
        self.pos = loc.get_tile(0, 0)
        self.animation_move_from = [0, 0]
        self.delay = 0
        self.gravity = 1
        self.collide = 1

    def __str__(self):
        return '[' + str(self.id) + ',' + self.name + ',' + str(self.seed) + ',' + \
               '[' + str(self.pos.x) + ',' + str(self.pos.y) + ']]'

    def load(self, p):
        self.id = p[0]
        self.seed = p[1]
        self.pos.load(p[2])
        return 3

    def remove(self):
        Turn.queue.remove(self)
        self.location.record.remove(self)
        self.pos.things.remove(self)

    def make_form(self, arg):
        self.form = Sprite(texture_name=arg)

    def draw(self, tile, surface, pos):
        self.animation_move_from[0] += (pos[0] - self.animation_move_from[0]) * .1
        y = pos[1] - self.animation_move_from[1]
        if y > 0:
            self.animation_move_from[1] += min(16, y)
        else:
            self.animation_move_from[1] += y * .1
        self.form.draw(surface, self.animation_move_from[0], self.animation_move_from[1])

    def turn(self):
        if self.gravity:
            moves = self.move(0, 8, Tile.CHECK_ANY)
            if moves:
                self.on_fall(moves)

    def relocate(self, x, y):
        old_pos = self.pos
        self.pos = self.location.get_tile(x, y)
        if self.pos != old_pos:
            old_pos.things.remove(self)
            self.pos.things.append(self)
            diff = (self.pos - old_pos)
            return abs(diff.x) + abs(diff.y)
        return 0

    def move(self, x, y, flag=Tile.CHECK_NONE):
        new_pos = self.location.collide_line(self.pos, x, y, flag)
        return self.relocate(new_pos.x, new_pos.y)

    def on_fall(self, distance):
        pass
