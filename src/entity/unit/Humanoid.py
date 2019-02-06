from src.entity.Space import Space
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit


class Humanoid(Unit):
    def __init__(self, form, seed, loc):
        super().__init__(form, seed, loc)
        self.form.randomize_clip('hit', 4)
        self.form.randomize_clip('dead1', 16)
        self.form.randomize_clip('dead2', 16)
        self.form.randomize_clip('dead3', 16)
        self.weapon = None
        self.armor = None
        self.aim_angle = 0

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        armor = '['+self.armor.__str__()+']'
        return super().__str__() + ',' + weapon + ',' + armor

    def load(self, p):
        index = super().load(p)
        if p[index]:
            weapon = Stock.get(p[index][3], self.location, p[index])
            weapon.interact(self)
        if p[index + 1]:
            armor = Stock.get(p[index+1][3], self.location, p[index+1])
            armor.use(self)
        return index + 2

    def make_fist(self):
        r = Stock.get('Fist', self.location)
        r.on_equip(self)
        return r

    def make_armor(self):
        r = Stock.get('Underwear', self.location)
        r.on_equip(self)
        return r

    def hit(self, hitter, damage):
        r = super().hit(hitter, damage)
        self.form.randomize_once(18)
        return r

    def face(self, direction):
        self.weapon.form.flip(-direction)
        super().face(direction)

    def draw(self, surface, pos):
        if self.weapon:
            x = self.animation_move_from[0] + self.form.organs[0].lower_joint.x
            y = self.animation_move_from[1] + self.form.organs[0].lower_joint.y - self.form.height
            self.weapon.form.draw(surface, x, y)
        super().draw(surface, pos)

    def drop(self):
        if self.is_armed():
            self.weapon.on_unequip()
        self.weapon = self.make_fist()

    def is_armed(self):
        return self.weapon.name != 'Fist'

    def aim(self):
        angle = Space(self.next_target).get_atan()
        self.weapon.form.rotation = angle + 180
