import pygame

from src.entity.Image import Image
from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Object(Image):
    BLOCK = 40

    def __init__(self, loc):
        super().__init__(Space())
        self.location = loc
        self.group = None
        self.pos = self.location.get_tile(0)
        self.delay = 0
        self.gravity = 0
        self.collision_type = Tile.COLLIDE_OBJECT
        self.visible = 1
        self.standables = Tile.CHECK_FOUNDATION.copy()
        self.removed = 0
        self.depth = 1
        self.falling = 0

    def __str__(self):
        r = Dialog.space(self.pos)
        return super().__str__() + ',' + r + ',' + self.name + ',' + self.group + ',' + self.form_name

    def load(self, p):
        index = super().load(p)
        if isinstance(p[index][0], list):
            p[index] = p[index][0]
        self.pos = self.location.get_tile(p[index])
        index += 1
        self.name = p[index]
        index += 1
        self.group = p[index]
        index += 1
        self.set_form(p[index])
        index += 1
        return index

    def add(self):
        self.removed = 0
        Turn.add(self.turn)
        self.relocate(self.pos.x, self.pos.y, force=1)
        self.location.record.append(self)
        return self

    def remove(self):
        self.removed = 1
        Turn.remove(self.turn)
        self.location.record.remove(self)
        self.pos.things.remove(self)
        del self

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.run_cache(arg)

    def draw(self, surface):
        diff = self.pos.get_center() - self.vec
        self.vec.x += diff.x * .07
        if 0 < diff.y and self.gravity:
            self.vec.y += min(16, diff.y)
        else:
            self.vec.y += diff.y * .07
        self.form.draw(surface, self.vec.x, self.vec.y)

    def turn(self):
        if self.is_fall():
            old = self.pos
            new = self.move(0, 4, flag=self.standables)
            if new != old:
                if self.pos.y > self.location.edge + 8:
                    self.out_of_bounds()
                else:
                    self.falling += new.y - old.y
                    if self.get_offset_tile(0, 1).is_land(self.standables):
                        self.on_fall()
            else:
                self.falling = 0

    def out_of_bounds(self):
        self.remove()

    def trigger(self):
        pass

    def is_fall(self):
        return self.gravity

    def on_fall(self):
        pass

    def get_offset_tile(self, x, y):
        return self.location.get_tile(self.pos + (x, y))

    def relocate(self, x, y, force=0):
        if force or x != self.pos.x or y != self.pos.y:
            diff = [x - self.pos.x, y - self.pos.y]
            self.location.get_tile(self.pos).things.remove(self)
            new = self.location.get_tile(self.pos + diff)
            new.things.append(self)
            self.pos = new
            if force:
                self.update_vec()
            return abs(diff[0]), abs(diff[1])
        return 0

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        new_pos = self.location.collide_land(self.pos, x, y, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def update_vec(self):
        self.vec.load(self.pos.get_center())

    def center_camera(self):
        Camera.target = self
