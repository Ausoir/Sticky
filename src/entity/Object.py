from src.entity.Image import Image
from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class Object(Image):
    BLOCK = 40

    def __init__(self, loc):
        super().__init__(Space())
        self.location = loc
        self.pos = [self.location.get_tile(0, 0)]
        self.delay = 0
        self.gravity = 1
        self.collide = Tile.COLLIDE_OBJECT
        self.visible = 1
        self.standables = Tile.CHECK_SUPPORTED
        self.removed = 0
        self.depth = 1

    def __str__(self):
        r = []
        for i in self.pos:
            r.append('[' + str(i.x) + ',' + str(i.y) + ']')
        return super().__str__() + ',[' + (','.join(r)) + '],' + self.name + ',' + self.form_name

    def load(self, p):
        index = super().load(p)
        self.pos = []
        for i in p[index]:
            self.pos.append(self.location.get_tile(i))
        index += 1
        self.name = p[index]
        index += 1
        self.make_form(p[index])
        index += 1
        return index

    def add(self):
        self.removed = 0
        Turn.add(self)
        self.relocate(self.pos[0].x, self.pos[0].y, force=1)
        self.location.record.append(self)
        return self

    def remove(self):
        self.removed = 1
        Turn.remove(self)
        self.location.record.remove(self)
        for i in self.pos:
            i.things.remove(self)

    def make_form(self, arg):
        self.form_name = arg
        self.form = Data.run_cache(arg)

    def draw(self, surface):
        if Camera.tile_in_camera(self.pos[0].x, self.pos[0].y):
            diff = self.pos[0].get_center() - self.vec
            self.vec.x += diff.x * .1
            if diff.y > 0 and self.gravity:
                self.vec.y += min(16, diff.y)
            else:
                self.vec.y += diff.y * .1
            self.form.draw(surface, self.vec.x, self.vec.y)
            return 1
        return 0

    def is_fall(self):
        return self.gravity

    def on_fall(self, distance):
        pass

    def turn(self):
        if self.is_fall():
            old = self.pos[0]
            new = self.move(0, 4, flag=self.standables)
            if new != old:
                if self.pos[0].y > self.location.edge:
                    self.remove()
                else:
                    self.on_fall(new.y - old.y)

    def get_offset_tile(self, x, y):
        return self.location.get_tile(self.pos[0] + (x, y))

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
                self.vec.load(self.pos[0].get_center())
            return abs(diff[0]), abs(diff[1])
        return 0

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        new_pos = self.location.collide_land(self.pos[0], x, y, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def center_camera(self):
        Camera.target = self.vec
