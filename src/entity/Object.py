from src.entity.Image import Image
from src.entity.Space import Space
from src.game import Global
from src.game.Camera import Camera
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools import Direction
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Object(Image):
    BLOCK = 40

    def __init__(self, loc):
        super().__init__(Space())
        self.location = loc
        self.class_name = None
        self.pos = self.location.get_tile(0)
        self.old_pos = self.pos
        self.delay = 0
        self.collision_type = Tile.COLLIDE_OBJECT
        self.removed = 0
        self.falling = 0
        self.in_sight = False

    def __str__(self):
        r = Dialog.space(self.pos)
        return super().__str__() + ',' + r + ',' + self.name + ',' + self.class_name + ',' + self.form_name

    def load(self, p):
        index = super().load(p)
        if isinstance(p[index][0], list):
            p[index] = p[index][0]
        self.pos = self.location.get_tile(p[index])
        index += 1
        self.name = p[index]
        index += 1
        self.class_name = p[index]
        index += 1
        self.set_form(p[index])
        index += 1
        return index

    def add(self):
        self.removed = 0
        self.form.show(True)
        Turn.add(self.turn)
        self.relocate(self.pos.x, self.pos.y, force=1)
        self.location.record.append(self)
        return self

    def remove(self):
        self.removed = 1
        self.form.show(False)
        Turn.remove(self.turn)
        self.location.record.remove(self)
        self.pos.things.remove(self)
        del self

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg)

    def set_row(self, row):
        self.form.z = 40 - row

    def update(self):
        diff = self.pos.get_center() - self.vec
        self.vec += diff * .07
        self.form.place(self.vec.x, self.vec.y)

    def turn(self):
        pass

    def show(self, visible):
        self.form.show(visible)

    def bound(self, visible):
        self.form.bound(visible)

    def out_of_bounds(self):
        from src.tools.Turnee import Turnee
        Turnee(self.remove, 0)

    def trigger(self):
        pass

    def get_offset_tile(self, x, y):
        return self.location.get_tile(self.pos + (x, y))

    def get_front_tile(self, direction, mag=1):
        coord = Direction.coord[direction]
        coord = [coord[0] * mag, coord[1] * mag]
        return self.location.get_tile(self.pos + coord)

    def relocate(self, x, y, force=0):
        if force or x != self.pos.x or y != self.pos.y:
            diff = [x - self.pos.x, y - self.pos.y]
            self.location.get_tile(self.pos).things.remove(self)
            new = self.location.get_tile(self.pos + diff)
            new.things.append(self)
            self.old_pos = self.pos
            self.pos = new
            if force:
                self.update_vec()
            return abs(diff[0]), abs(diff[1])
        return 0

    def move_toward(self, direction, mag=1, distance=1, flag=Tile.CHECK_LARGE):
        coord = Direction.coord[direction]
        coord = [coord[0] * mag, coord[1] * mag]
        target = self.pos + coord
        new_pos = self.location.collide_land(self.pos, target, flag=flag, distance=distance)
        moved = self.pos != new_pos
        self.relocate(new_pos.x, new_pos.y)
        return moved

    def move(self, x, y, distance=8, flag=Tile.CHECK_LARGE):
        target = self.pos + (x, y)
        new_pos = self.location.collide_land(self.pos, target, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def update_vec(self):
        self.vec.load(self.pos.get_center())

    def center_camera(self):
        Camera.target = self
        Global.map_view.on_sight_change()
