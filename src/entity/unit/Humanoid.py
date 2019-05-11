from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.game.Camera import Camera


class Humanoid(Unit):
    def __init__(self, loc):
        super().__init__(loc)
        self.weapon = None
        self.offhand = None
        self.armor = None
        self.headgear = None
        self.aim_angle = 0
        self.gold = 0
        self.hang = 0
        self.fist = Stock.get('Fist')
        self.body = Stock.get('Body')
        self.head = Stock.get('Head')

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        offhand = '['+self.offhand.__str__()+']'
        armor = '['+self.armor.__str__()+']'
        headgear = '['+self.headgear.__str__()+']'
        gear = weapon + ',' + offhand + ',' + armor + ',' + headgear
        return super().__str__() + ',' + str(self.gold) + ',' + gear

    def load(self, p):
        index = super().load(p)
        self.form.randomize_clip('hit', 4)
        self.gold = p[index]
        index += 1
        if p[index]:
            weapon = Stock.get(p[index][2], p[index])
            weapon.on_equip(self)
        else:
            self.make_fist()
        index += 1
        if p[index]:
            offhand = Stock.get(p[index][2], p[index])
            weapon = self.weapon
            offhand.on_equip(self)
            self.offhand = self.weapon
            self.weapon = weapon
        else:
            weapon = self.weapon
            self.make_fist()
            self.offhand = self.weapon
            self.weapon = weapon
        self.armor = self.body
        self.headgear = self.head
        index += 1
        if p[index]:
            armor = Stock.get(p[index][2], p[index])
            armor.use(self)
        else:
            self.make_armor()
        index += 1
        if p[index]:
            headgear = Stock.get(p[index][2], p[index])
            headgear.use(self)
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

    def is_fall(self):
        return self.gravity and not self.hang

    def update_durability(self, damage=0):
        head_armor, damage = self.headgear.get_reduction(damage)
        if 0 < damage >= head_armor == 0 and self.headgear.durability != -1:
            self.headgear.die()
        armor, damage = self.armor.get_reduction(damage)
        if self.weapon.durability == 0:
            self.weapon.die()
        self.durability = head_armor + armor + 1

    def is_hit(self, faction=0):
        if super().is_hit(faction):
            if self.action.current_action != 'dodge':
                return 1
            else:
                self.action.exert(1, 1)
                self.form.randomize_once(16)

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
        if self.direction != direction:
            self.weapon.form.flip(1, 0)
        self.weapon.form.rotate(100 * direction)
        super().face(direction)

    def draw(self, surface):
        if Camera.tile_in_camera(self.pos[0].x, self.pos[0].y):
            x = self.vec.x + self.form.organs[0].lower_joint.x
            y = self.vec.y + self.form.organs[0].lower_joint.y - self.form.height
            arm = -(self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
            self.weapon.form.rotate(arm + 90 + (self.weapon.rotation * self.direction))
            self.weapon.form.draw(surface, x, y)
            r = super().draw(surface)
            x = self.vec.x + self.form.organs[5].lower_joint.x
            y = self.vec.y + self.form.organs[5].lower_joint.y - self.form.height
            arm = -(self.form.organs[5].lower_joint - self.form.organs[5].upper_joint).get_atan()
            self.offhand.form.rotate(arm + 110 + (self.offhand.rotation * self.direction))
            self.offhand.form.draw(surface, x, y)
            return r
        return 0

    def clean_buffs(self, force=0):
        r = super().clean_buffs(force)
        r = r or self.weapon.clean_buffs(force)
        r = r or self.armor.clean_buffs(force)
        return r

    def make_fist(self):
        self.fist.on_equip(self)

    def make_armor(self):
        self.armor = self.body
        self.armor.use(self)

    def make_headgear(self):
        self.headgear = self.head
        self.headgear.use(self)

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

    def is_armored(self):
        return self.armor.name != 'Body'

    def is_headgeared(self):
        return self.headgear.name != 'Head'
