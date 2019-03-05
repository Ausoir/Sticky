from src.game.Global import DEPTH_OBJECT
from src.entity.Space import Space
from src.game.Camera import Camera
from src.game.Group import Group
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Data import Data


class Object:
    BLOCK = 40

    def __init__(self, loc):
        self.id = 0
        self.name = None
        self.form_name = ''
        self.form = None
        self.location = loc
        self.pos = [self.location.get_tile(0, 0)]
        self.motion_pos = Space()
        self.delay = 0
        self.gravity = 1
        self.collide = Tile.COLLIDE_OBJECT
        self.depth = DEPTH_OBJECT
        self.visible = 1

    def __str__(self):
        r = []
        for i in self.pos:
            r.append('[' + str(i.x) + ',' + str(i.y) + ']')
        return str(self.id) + ',[' + (','.join(r)) + '],' + self.name + ',' + self.form_name

    def load(self, p):
        self.id = p[0]
        self.pos = []
        for i in p[1]:
            self.pos.append(self.location.get_tile(i))
        self.name = p[2]
        self.make_form(p[3])
        return 4

    def add(self):
        Group.objects.add(self)
        Turn.add(self)
        self.relocate(self.pos[0].x, self.pos[0].y, 1)
        self.location.record.append(self)
        return self

    def remove(self):
        Group.remove(self)
        Turn.remove(self)
        self.location.record.remove(self)
        for i in self.pos:
            i.things.remove(self)

    def make_form(self, arg):
        self.form_name = arg
        self.form = Data.run_cache(arg)

    def draw(self, surface):
        if Camera.tile_in_camera(self.pos[0].x, self.pos[0].y):
            pos = self.pos[0].get_center()
            self.motion_pos.x += (pos.x - self.motion_pos.x) * .1
            y = pos.y - self.motion_pos.y
            if y > 0 and self.gravity:
                self.motion_pos.y += min(16, y)
            else:
                self.motion_pos.y += y * .1
            self.form.draw(surface, self.motion_pos.x, self.motion_pos.y)
            return 1
        return 0

    def is_fall(self):
        return self.gravity

    def turn(self):
        if self.is_fall():
            old = self.pos[0]
            new = self.move(0, 4, flag=Tile.CHECK_LANDABLE)
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
                self.motion_pos.load(self.pos[0].get_center())
            return abs(diff[0]), abs(diff[1])
        return 0

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        new_pos = self.location.collide_line(self.pos[0], x, y, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def on_fall(self, distance):
        pass

    def center_camera(self):
        Camera.target = self.motion_pos
