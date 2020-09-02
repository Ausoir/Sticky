from src.entity.Image import Image
from src.game import Global
from src.map.Tile import Tile


class Object(Image):
    BLOCK = 40

    def __init__(self):
        super().__init__()
        self.class_name = None
        self.pos = None
        self.pos_offset = (0, 0)
        self.save = True
        self.obstruct_type = Tile.COLLIDE_OBJECT
        self.collision_type = Tile.COLLIDE_UNIT
        self.removed = 1

    def __str__(self):
        space = '[' + str(self.pos.x - self.pos_offset[0]) + ',' + str(self.pos.y - self.pos_offset[1]) + ']'
        return space + ',' + self.name + ',' + self.class_name + ',' + self.form_name

    def load(self, p):
        index = 0
        if isinstance(p[index][0], list):
            p[index] = p[index][0]
        self.pos = Global.world.location.get_tile(p[index][0], p[index][1], limit=True)
        index += 1
        self.name = p[index]
        index += 1
        self.class_name = p[index]
        index += 1
        self.set_form(p[index])
        index += 1
        return index

    def add(self):
        if self.removed == 1:
            self.removed = 0
            Global.world.location.population.add(self)
            self.show(True)
            self.relocate(to=self.pos, force=True)
            return self

    def remove(self):
        if self.removed == 0:
            Global.world.location.population.remove(self)
            self.removed = 1
            self.bound(False)
            self.show(False)
            self.pos.things.remove(self)
            del self
            return True

    def set_row(self, row):
        self.form.z = row * 20 + 100

    def update(self):
        diff = self.pos.get_center() - self.vec
        self.vec += diff * .2
        super().update()

    def show(self, visible):
        self.form.show(visible)

    def bound(self, visible):
        self.form.bound(visible)

    def trigger(self):
        pass

    def relocate(self, to=None, x=None, y=None, force=False):
        if to is None:
            to = Global.world.location.get_tile(x, y, limit=True)
        if force or to != self.pos:
            self.pos.things.remove(self)
            to.things.append(self)
            self.pos = to
            if force:
                self.update_vec()
            elif self.pos.get_icon() == '~':
                self.drown()
            if self.pos not in Global.map_view.in_bounds:
                Global.map_view.in_bounds.append(self.pos)
            return True

    def deregister(self):
        self.pos.things.remove(self)

    def drown(self):
        pass

    def move_line(self, to, flag=None):
        if flag is None:
            flag = self.collision_type
        new_pos = Global.world.location.collide_land(self.pos, to, flag=flag, distance=-1)
        moved = self.pos != new_pos
        if moved:
            self.relocate(to=new_pos)
        return moved

    def update_vec(self):
        self.vec.load(self.pos.get_center())

    def adjust_pos(self, x, y):
        self.relocate(x=self.pos.x + x, y=self.pos.y + y)
        self.vec.x += x * Global.BLOCK
        self.vec.y += y * Global.BLOCK
        self.bound(False)
