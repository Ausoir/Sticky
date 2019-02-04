from src.form.Sprite import Sprite


# Has form, has tile position
from src.game.Turn import Turn
from src.map.Tile import Tile


class Object:
    BLOCK = 40

    def __init__(self, form, seed, loc):
        self.id = 0
        self.name = 'none'
        self.seed = seed
        self.form = None
        self.make_form(form)
        self.location = loc
        self.pos = [self.location.get_tile(0, 0)]
        self.animation_move_from = [0, 0]
        self.delay = 0
        self.gravity = 1
        self.collide = Tile.CHECK_ANY

    def __str__(self):
        r = []
        for i in self.pos:
            r.append('[' + str(i.x) + ',' + str(i.y) + ']')
        return str(self.id) + ',' + self.name + ',' + str(self.seed) + ',[' + (','.join(r)) + ']'

    def load(self, p):
        self.id = p[0]
        self.name = p[1]
        self.seed = p[2]
        self.pos = []
        for i in p[3]:
            self.pos.append(self.location.get_tile(i))
        return 4

    def add(self):
        Turn.add(self)
        self.relocate(self.pos[0].x, self.pos[0].y, 1)
        self.location.record.append(self)
        return self

    def remove(self):
        Turn.remove(self)
        self.location.record.remove(self)
        for i in self.pos:
            i.things.remove(self)

    def make_form(self, arg):
        self.form = Sprite(texture_name=arg)

    def draw(self, surface, pos):
        self.animation_move_from[0] += (pos[0] - self.animation_move_from[0]) * .1
        y = pos[1] - self.animation_move_from[1]
        if y > 0 and self.gravity:
            self.animation_move_from[1] += min(16, y)
        else:
            self.animation_move_from[1] += y * .1
        self.form.draw(surface, self.animation_move_from[0], self.animation_move_from[1])

    def turn(self):
        if self.gravity:
            old = self.pos[0]
            new = self.move(0, 8)
            if new != old:
                self.on_fall(new.y - old.y)

    def relocate(self, x, y, force=0):
        if force or x != self.pos[0].x or y != self.pos[0].y:
            diff = [x - self.pos[0].x, y - self.pos[0].y]
            new_pos = []
            for i in self.pos:
                self.location.get_tile(i).things.remove(self)
                new = self.location.get_tile(i + diff)
                new.things.append(self)
                new_pos.append(new)
            self.pos = new_pos
            if force:
                vec = self.pos[0].get_vec()
                self.animation_move_from[0] = vec[0]
                self.animation_move_from[1] = vec[1]
            return abs(diff[0]), abs(diff[1])
        return 0

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        new_pos = self.location.collide_line(self.pos[0], x, y, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def on_fall(self, distance):
        pass
