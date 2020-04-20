from src.entity.Image import Image
from src.map.Tile import Tile
from src.tools.Dialog import Dialog


class Object(Image):
    BLOCK = 40

    def __init__(self, location):
        super().__init__()
        self.location = location
        self.class_name = None
        self.destination = None
        self.pos = None
        self.save = True
        self.obstruct_type = Tile.COLLIDE_OBJECT
        self.collision_type = Tile.CHECK_SOLID
        self.removed = 1

    def __str__(self):
        r = Dialog.space(self.pos)
        return super().__str__() + ',' + r + ',' + self.name + ',' + self.class_name + ',' + self.form_name

    def load(self, p):
        index = super().load(p)
        if isinstance(p[index][0], list):
            p[index] = p[index][0]
        self.pos = self.location.get_tile(p[index][0], p[index][1], limit=True)
        self.destination = self.pos
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
            self.show(True)
            self.relocate(to=self.pos, force=True)
            self.location.population.add(self)
            return self

    def remove(self):
        if self.removed == 0:
            self.removed = 1
            self.show(False)
            self.location.population.remove(self)
            self.pos.things.remove(self)
            del self

    def set_row(self, row):
        self.form.z = row * 20 + 100

    def update(self):
        diff = self.destination.get_center() - self.vec
        self.vec += diff * .08
        super().update()

    def show(self, visible):
        self.form.show(visible)

    def bound(self, visible):
        self.form.bound(visible)

    def trigger(self):
        pass

    def relocate(self, to=None, x=None, y=None, force=False):
        if to is None:
            to = self.location.get_tile(x, y, limit=True)
        if force or to != self.pos:
            self.pos.things.remove(self)
            to.things.append(self)
            self.pos = to
            self.destination = to
            if force:
                self.update_vec()
            return True
        return 0

    def move_line(self, to, flag=None):
        if flag is None:
            flag = self.collision_type
        new_pos = self.location.collide_land(self.pos, to, flag=flag, distance=-1)
        moved = self.pos != new_pos
        if moved:
            self.relocate(to=new_pos)
        else:
            self.destination = self.pos
        return moved

    def update_vec(self):
        self.vec.load(self.pos.get_center())
