from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.game.Camera import Camera


class Humanoid(Unit):
    fist = Stock.get('Fist')
    body = Stock.get('Body')
    head = Stock.get('Head')

    def __init__(self, loc):
        super().__init__(loc)
        self.weapon = None
        self.armor = None
        self.headgear = None
        self.aim_angle = 0
        self.gold = 0
        self.hang = 0

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']'
        armor = '['+self.armor.__str__()+']'
        headgear = '['+self.headgear.__str__()+']'
        return super().__str__() + ',' + str(self.gold) + ',' + weapon + ',' + armor + ',' + headgear

    def load(self, p):
        index = super().load(p)
        self.form.randomize_clip('hit', 4)
        self.form.randomize_clip('dead1', 12)
        self.form.randomize_clip('dead2', 12)
        self.form.randomize_clip('dead3', 12)
        self.gold = p[index]
        if p[index + 1]:
            weapon = Stock.get(p[index + 1][2], p[index + 1])
            weapon.on_equip(self)
        else:
            self.make_fist()
        self.armor = Humanoid.body
        self.headgear = Humanoid.head
        if p[index + 2]:
            armor = Stock.get(p[index + 2][2], p[index + 2])
            armor.use(self)
        else:
            self.make_armor()
        if p[index + 3]:
            headgear = Stock.get(p[index + 3][2], p[index + 3])
            headgear.use(self)
        else:
            self.make_headgear()
        self.update_durability()
        return index + 4

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
        if 0 < damage >= head_armor == 0:
            self.headgear.die()
        armor, damage = self.armor.get_reduction(damage)
        if 0 < damage >= armor == 0:
            self.armor.die()
        if self.weapon.durability == 0:
            self.weapon.die()
        self.durability = head_armor + armor + 1

    def hit(self, damage):
        r = super().hit(damage)
        self.form.randomize_once(18)
        self.update_durability(damage)
        return r

    def die(self):
        self.drop()
        super().die()

    def face(self, direction):
        self.weapon.form.face(direction)
        self.weapon.form.rotation = 100 * direction
        super().face(direction)

    def draw(self, surface):
        if Camera.tile_in_camera(self.pos[0].x, self.pos[0].y):
            x = self.motion_pos.x + self.form.organs[0].lower_joint.x
            y = self.motion_pos.y + self.form.organs[0].lower_joint.y - self.form.height
            self.weapon.form.draw(surface, x, y)
            return super().draw(surface)
        return 0

    def clean_buffs(self, force=0):
        r = super().clean_buffs(force)
        r = r or self.weapon.clean_buffs(force)
        r = r or self.armor.clean_buffs(force)
        return r

    def make_fist(self):
        Humanoid.fist.on_equip(self)

    def make_armor(self):
        self.armor = Humanoid.body
        self.armor.use(self)

    def make_headgear(self):
        self.headgear = Humanoid.head
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

    def aim(self):
        angle = self.next_target.get_atan()
        self.weapon.form.rotation = angle - 90
