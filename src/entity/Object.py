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

    def __init__(self):
        super().__init__(Space())
        self.class_name = None
        self.pos = None
        self.old_pos = self.pos
        self.obstruct_type = Tile.COLLIDE_OBJECT
        self.collision_type = Tile.CHECK_FIRM
        self.removed = 0
        self.falling = 0
        self.in_sight = False
        from src.map import Depth
        self.depth = Depth.object_depth

    def __str__(self):
        r = Dialog.space(self.pos)
        return super().__str__() + ',' + r + ',' + self.name + ',' + self.class_name + ',' + self.form_name

    def load(self, p):
        index = super().load(p)
        if isinstance(p[index][0], list):
            p[index] = p[index][0]
        self.pos = Global.location.get_tile(p[index])
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
        Global.location.population.add(self)
        return self

    def remove(self):
        self.removed = 1
        self.show(False)
        Turn.remove(self.turn)
        Global.location.population.remove(self)
        self.pos.things.remove(self)
        del self

    def set_form(self, arg):
        self.form_name = arg
        self.form = Data.get_form(arg)

    def set_row(self, row):
        self.form.z = self.depth(row)

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

    def get_direction_toward(self, pos):
        diff = pos - self.pos
        horizontal = abs(diff.x) >= abs(diff.y)
        if horizontal:
            if diff.x < 0:
                return 1
            else:
                return 3
        else:
            if diff.y < 0:
                return 2
            else:
                return 4

    def get_front_tile(self, direction, mag=1):
        coord = Direction.coord[direction]
        return self.pos.get_neighbor(coord[0] * mag, coord[1] * mag)

    def relocate(self, x, y, force=0):
        if force or x != self.pos.x or y != self.pos.y:
            diff = [x - self.pos.x, y - self.pos.y]
            Global.location.get_tile(self.pos).things.remove(self)
            new = Global.location.get_tile(self.pos + diff)
            new.things.append(self)
            self.old_pos = self.pos
            self.pos = new
            if force:
                self.update_vec()
            return abs(diff[0]), abs(diff[1])
        return 0

    def move_toward(self, direction, distance=1, flag=None):
        coord = Direction.coord[direction]
        target = self.pos + coord
        flag = flag or self.collision_type
        new_pos = Global.location.collide_land(self.pos, target, flag=flag, distance=distance)
        moved = self.pos != new_pos
        self.relocate(new_pos.x, new_pos.y)
        return moved

    def move(self, x, y, distance=8, flag=None):
        target = self.pos + (x, y)
        flag = flag or self.collision_type
        new_pos = Global.location.collide_land(self.pos, target, distance=distance, flag=flag)
        self.relocate(new_pos.x, new_pos.y)
        return new_pos

    def update_vec(self):
        self.vec.load(self.pos.get_center())

    def center_camera(self):
        Camera.target = self
        Global.map_view.on_sight_change()
