from src.entity.Space import Space
from src.entity.unit.Unit import Unit
from src.entity.Stock import Stock


class Humanoid(Unit):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)
        self.pos.append(self.location.get_tile(0, -1))
        self.form.randomize_clip('hit', 4)
        self.form.randomize_clip('dead1', 16)
        self.form.randomize_clip('dead2', 16)
        self.form.randomize_clip('dead3', 16)
        self.weapon = self.make_fist()
        self.aim_angle = 0

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        return super().__str__() + ',' + weapon

    def load(self, p):
        index = super().load(p)
        if p[index]:
            weapon = Stock.get(p[index][1], self.location)
            weapon.load(p[index])
            self.pickup(weapon)
        return index + 1

    def make_fist(self):
        r = Stock.get('fist', self.location)
        r.on_equip(self)
        return r

    def input(self, action, target):
        super().input(action, [target[0], target[1] + 1])

    def get_interact_pos(self):
        if self.pos.__len__() > 1:
            return self.pos[1]
        else:
            return self.location.get_tile(self.pos[0] + (0, -1))

    def hit(self, hitter, damage):
        r = super().hit(hitter, damage)
        self.form.randomize_once(18)
        return r

    def face(self, direction):
        if self.weapon and direction != self.direction:
            self.weapon.form.rotation += 180
        super().face(direction)

    def draw(self, surface, pos):
        if self.weapon:
            x = self.animation_move_from[0] + self.form.organs[0].edge.x
            y = self.animation_move_from[1] + self.form.organs[0].edge.y - self.form.organs[0].height
            self.weapon.form.draw(surface, x, y)
        super().draw(surface, pos)

    def pickup(self, item):
        item.on_equip(self)
        self.weapon = item

    def drop(self):
        self.weapon.on_unequip(self)
        self.weapon = self.make_fist()

    def is_armed(self):
        return self.weapon.name != 'fist'

    def aim(self):
        angle = Space(self.next_target).get_atan()
        self.weapon.form.rotation = angle + 180
