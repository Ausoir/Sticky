from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit


class Humanoid(Unit):
    def __init__(self, loc):
        super().__init__(loc)
        self.weapon = None
        self.armor = None
        self.headgear = None
        self.aim_angle = 0
        self.gold = 0

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        armor = '['+self.armor.__str__()+']'
        headgear = '['+self.headgear.__str__()+']'
        return super().__str__() + ',' + str(self.gold) + ',' + weapon + ',' + armor + ',' + headgear

    def load(self, p):
        index = super().load(p)
        self.form.randomize_clip('hit', 4)
        self.form.randomize_clip('dead1', 16)
        self.form.randomize_clip('dead2', 16)
        self.form.randomize_clip('dead3', 16)
        self.gold = p[index]
        if p[index + 1]:
            weapon = Stock.get(p[index + 1][2], self.location, p[index + 1])
            weapon.interact(self)
        else:
            self.weapon = self.make_fist()
        if p[index + 2]:
            armor = Stock.get(p[index + 2][2], self.location, p[index + 2])
            armor.use(self)
        else:
            self.armor = self.make_armor()
        if p[index + 3]:
            headgear = Stock.get(p[index + 3][2], self.location, p[index + 3])
            headgear.use(self)
        else:
            self.headgear = self.make_headgear()
        return index + 4

    def turn(self):
        super().turn()
        self.weapon.states.update()

    def make_fist(self):
        r = Stock.get('Fist', self.location)
        r.on_equip(self)
        return r

    def make_armor(self):
        r = Stock.get('Body', self.location)
        r.use(self)
        return r

    def make_headgear(self):
        r = Stock.get('Head', self.location)
        r.use(self)
        return r

    def hit(self, damage):
        r = super().hit(damage)
        self.form.randomize_once(18)
        return r

    def face(self, direction):
        self.weapon.form.flip(-direction)
        super().face(direction)

    def draw(self, surface):
        x = self.motion_pos.x + self.form.organs[0].lower_joint.x
        y = self.motion_pos.y + self.form.organs[0].lower_joint.y - self.form.height
        self.weapon.motion_pos.load(x, y)
        self.weapon.form.draw(surface, x, y)
        super().draw(surface)

    def drop(self):
        if self.is_armed():
            self.weapon.relocate(self.pos[0].x, self.pos[0].y, force=1)
            self.weapon.on_unequip()
            self.weapon = self.make_fist()
            return 1
        return 0

    def unarmor(self):
        if self.is_armored():
            self.armor.relocate(self.pos[0].x, self.pos[0].y, force=1)
            self.armor.on_unequip()
            self.armor = self.make_armor()
            return 1
        return 0

    def unheadgear(self):
        if self.is_headgeared():
            self.headgear.relocate(self.pos[0].x, self.pos[0].y, force=1)
            self.headgear.on_unequip()
            self.headgear = self.make_headgear()
            return 1
        return 0

    def is_armed(self):
        return self.weapon.name != 'Fist'

    def is_armored(self):
        return self.armor.name != 'Body'

    def is_headgeared(self):
        return self.headgear.name != 'Head'

    def aim(self):
        angle = self.next_target.get_atan()
        self.weapon.form.rotation = angle + 180
