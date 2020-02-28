from src.entity.Image import Image
from src.game import Global
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools import Direction
from src.tools.Dialog import Dialog


class Object(Image):
    BLOCK = 40

    def __init__(self, location):
        super().__init__()
        self.location = location
        self.class_name = None
        self.pos = None
        self.old_pos = self.pos
        self.save = True
        self.obstruct_type = Tile.COLLIDE_OBJECT
        self.collision_type = Tile.CHECK_SOLID
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
        self.pos = self.location.get_tile(p[index][0], p[index][1], limit=True)
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
        self.show(True)
        Turn.add(self.turn)
        self.relocate(self.pos.x, self.pos.y, force=1)
        self.location.population.add(self)
        return self

    def remove(self):
        self.removed = 1
        self.show(False)
        Turn.remove(self.turn)
        self.location.population.remove(self)
        self.pos.things.remove(self)
        del self

    def set_row(self, row):
        self.form.z = row * 20 + 100

    def update(self):
        diff = self.pos.get_center() - self.vec
        self.vec += diff * .07
        super().update()

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

    def get_front_tile(self, direction, mag=1, limit=False):
        coord = Direction.coord[direction]
        return self.pos.get_neighbor(coord[0] * mag, coord[1] * mag, limit=limit)

    def relocate(self, x, y, force=0):
        if force or x != self.pos.x or y != self.pos.y:
            diff = [x - self.pos.x, y - self.pos.y]
            self.pos.things.remove(self)
            new = self.location.get_tile(self.pos.x + diff[0], self.pos.y + diff[1], limit=True)
            new.things.append(self)
            self.old_pos = self.pos
            self.pos = new
            if force:
                self.update_vec()
            return abs(diff[0]), abs(diff[1])
        return 0

    def move_toward(self, direction, distance=1, flag=None):
        coord = Direction.coord[direction]
        target = self.pos + [coord[0] * distance, coord[1] * distance]
        if flag is None:
            flag = self.collision_type
        new_pos = self.location.collide_land(self.pos, target, flag=flag, distance=distance)
        moved = self.pos != new_pos
        if new_pos:
            self.relocate(new_pos.x, new_pos.y)
        return moved

    def move(self, x, y, distance=8, flag=None):
        target = self.pos + (x, y)
        if flag is None:
            flag = self.collision_type
        new_pos = self.location.collide_land(self.pos, target, distance=distance, flag=flag)
        if new_pos:
            self.relocate(new_pos.x, new_pos.y)
            return new_pos

    def update_vec(self):
        self.vec.load(self.pos.get_center())
