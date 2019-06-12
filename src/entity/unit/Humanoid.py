from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit


class Humanoid(Unit):
    def __init__(self, loc):
        super().__init__(loc)
        self.armor = None
        self.headgear = None
        self.aim_angle = 0
        self.fist = Stock.get('Fist')
        self.body = Stock.get('Body')
        self.head = Stock.get('Head')
        self.weapon = self.fist
        self.offhand = self.fist

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        offhand = '['+self.offhand.__str__()+']'
        armor = '['+self.armor.__str__()+']'
        headgear = '['+self.headgear.__str__()+']'
        gear = weapon + ',' + offhand + ',' + armor + ',' + headgear
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        self.form.randomize_clip('hit', 4)
        if p[index]:
            weapon = Stock.get(p[index][2], p[index])
            weapon.on_equip(self)
        index += 1
        if p[index]:
            offhand = Stock.get(p[index][2], p[index])
            weapon = self.weapon
            offhand.on_equip(self)
            self.offhand = self.weapon
            self.weapon = weapon
        self.armor = self.body
        self.headgear = self.head
        index += 1
        if p[index]:
            armor = Stock.get(p[index][2], p[index])
            armor.host = self
            armor.use()
        else:
            self.make_armor()
        index += 1
        if p[index]:
            headgear = Stock.get(p[index][2], p[index])
            headgear.host = self
            headgear.use()
        else:
            self.make_headgear()
        self.update_durability()
        self.pilot.strategize()
        index += 1
        return index

    def turn(self):
        super().turn()
        self.weapon.states.update()

    def relocate(self, x, y, force=0):
        super().relocate(x, y, force)
        if self.is_armed():
            self.weapon.pos[0] = self.pos[0]

    def update_durability(self, damage=0):
        head_armor, damage = self.headgear.get_reduction(damage)
        if 0 < damage >= head_armor == 0 and self.headgear.durability != -1:
            self.headgear.die()
        armor, damage = self.armor.get_reduction(damage)
        if self.weapon.durability == 0:
            self.weapon.die()
        self.durability = head_armor + armor + 1

    def hit(self, damage):
        r = super().hit(damage)
        self.form.randomize_once(16)
        if self.durability > 0:
            self.update_durability(damage)
        return r

    def die(self):
        self.drop()
        super().die()

    def face(self, direction):
        self.weapon.face(direction)
        self.offhand.face(direction)
        super().face(direction)

    def draw(self, surface):
        x = self.vec.x + self.form.organs[0].lower_joint.x
        y = self.vec.y + self.form.organs[0].lower_joint.y - self.form.height
        arm = -(self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
        self.weapon.form.rotate(arm + 90 + (self.weapon.rotation * self.direction))
        self.weapon.form.draw(surface, x, y)
        super().draw(surface)
        x = self.vec.x + self.form.organs[5].lower_joint.x
        y = self.vec.y + self.form.organs[5].lower_joint.y - self.form.height
        arm = -(self.form.organs[5].lower_joint - self.form.organs[5].upper_joint).get_atan()
        self.offhand.form.rotate(arm + 110 + (self.offhand.rotation * self.direction))
        self.offhand.form.draw(surface, x, y)

    def on_block(self):
        self.action.exert(1, self.offhand.damage)
        return self.offhand.weight + 1

    def make_fist(self):
        self.fist.on_equip(self)

    def make_armor(self):
        self.armor = self.body
        self.armor.host = self
        self.armor.use()

    def make_headgear(self):
        self.headgear = self.head
        self.headgear.host = self
        self.headgear.use()

    def swap(self):
        weapon = self.offhand
        self.offhand = self.weapon
        self.weapon = weapon

    def drop(self):
        if self.is_armed():
            self.weapon.on_unequip()
            self.make_fist()

    def unarmor(self):
        if self.is_armored():
            self.armor.relocate(self.pos[0].x, self.pos[0].y, force=1)
            self.armor.on_unequip()
            self.make_armor()
            self.update_durability()
            return 1
        return 0

    def unheadgear(self):
        if self.is_headgeared():
            self.headgear.relocate(self.pos[0].x, self.pos[0].y, force=1)
            self.headgear.on_unequip()
            self.make_headgear()
            return 1
        return 0

    def is_armed(self):
        return self.weapon.name != 'Fist'

    def is_shielded(self):
        return self.offhand.name != 'Fist'

    def is_armored(self):
        return self.armor.name != 'Body'

    def is_headgeared(self):
        return self.headgear.name != 'Head'

    def get_accessibles(self):
        r = self.pos[0].things.copy()
        r += self.armor.items
        r.append(self.weapon)
        r.append(self.offhand)
        return r
