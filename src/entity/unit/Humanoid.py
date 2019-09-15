from src.entity.unit.Unit import Unit
from src.game import Global
from src.game.Interaction import Interaction


class Humanoid(Unit):
    faces = []

    def __init__(self, loc):
        super().__init__(loc)
        self.armor = None
        self.headgear = None
        self.aim_angle = 0
        from src.entity.Stock import Stock
        self.fist = Stock.get('Fist')
        self.body = Stock.get('Body')
        self.head = Stock.get('Head')
        self.weapon = self.fist
        self.offhand = self.fist
        self.fist.host = self
        self.body.host = self
        self.head.host = self

    def __str__(self):
        weapon = '['+self.weapon.__str__()+']' if self.is_armed() else '0'
        offhand = '['+self.offhand.__str__()+']' if self.is_shielded() else '0'
        armor = '['+self.armor.__str__()+']' if self.is_armored() else '0'
        headgear = '['+self.headgear.__str__()+']' if self.is_headgeared() else '0'
        gear = weapon + ',' + offhand + ',' + armor + ',' + headgear
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        from src.entity.Stock import Stock
        from src.tools.Data import Data
        self.form.randomize_clip('hit', 4)
        head = Data.run_cache(Humanoid.faces[self.attributes.gene % len(Humanoid.faces)])
        self.form.organs[3].set(head)
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
        self.update_durability(0)
        index += 1
        for i in self.get_possessions():
            i.id = Stock.location.get_id()
        return index

    def turn(self):
        super().turn()
        if self.action.current_action == 'idle':
            self.weapon.rotation = 60
        self.weapon.states.update()

    def use(self):
        if Interaction.interact(self.weapon):
            self.action.set('wait')
        else:
            self.weapon.use()

    def relocate(self, x, y, force=0):
        super().relocate(x, y, force)
        if self.is_armed():
            self.weapon.pos = self.pos

    def update_durability(self, damage):
        head_armor, damage = self.headgear.get_reduction(damage)
        if 0 < damage >= head_armor == 0 and self.headgear.durability != -1:
            self.headgear.die()
        armor, damage = self.armor.get_reduction(damage)
        if armor == 0 and self.armor.durability != -1:
            self.armor.die()
        if self.weapon.durability == 0:
            self.weapon.die()
        self.durability = head_armor + armor + 1

    def hit(self, damage):
        r = super().hit(damage)
        self.form.randomize_once(8)
        self.offhand.hit(1)
        if self.durability > 0:
            self.update_durability(damage)
        return r

    def die(self):
        self.drop()
        super().die()

    def face(self, direction):
        self.weapon.face(direction)
        self.offhand.face(direction)
        self.headgear.face(direction)
        super().face(direction)

    def draw(self, surface):
        vec_y = self.vec.y + Global.HALF_BLOCK
        x = self.vec.x + self.form.organs[0].lower_joint.x
        y = vec_y + self.form.organs[0].lower_joint.y + 2
        arm = -(self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
        self.weapon.form.rotate(arm + 90 + (self.weapon.rotation * self.direction))
        self.weapon.form.draw(surface, x, y)
        super().draw(surface)
        if self.headgear.visible:
            x = self.vec.x + self.form.organs[3].upper_joint.x
            y = vec_y + self.form.organs[3].upper_joint.y
            arm = -(self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
            self.headgear.form.pivot.y = self.headgear.form.size.y
            self.headgear.form.rotate(arm - 90)
            self.headgear.form.draw(surface, x, y)
        x = self.vec.x + self.form.organs[5].lower_joint.x
        y = vec_y + self.form.organs[5].lower_joint.y
        arm = -(self.form.organs[5].lower_joint - self.form.organs[5].upper_joint).get_atan()
        self.offhand.form.rotate(arm + 110 + (self.offhand.rotation * self.direction))
        self.offhand.form.draw(surface, x, y)

    def get_dodge(self):
        if self.action.current_action == 'down':
            return 0
        r = self.get_proficiency('dodge') + self.armor.armor
        if self.action.current_action == 'block':
            if self.get_proficiency('block'):
                return self.offhand.weight * 10 + 10
            else:
                r += self.offhand.weight * 4 + 4
        return r

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
            self.armor.relocate(self.pos.x, self.pos.y, force=1)
            self.armor.on_unequip()
            self.make_armor()
            self.update_durability(0)
            return 1
        return 0

    def unheadgear(self):
        if self.is_headgeared():
            self.headgear.relocate(self.pos.x, self.pos.y, force=1)
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

    def get_possessions(self):
        r = [self.weapon]
        r += self.armor.items
        r.append(self.headgear)
        r.append(self.armor)
        return r

    def get_accessibles(self):
        r = []
        from src.entity.unit.item.Item import Item
        for thing in self.pos.things:
            if isinstance(thing, Item):
                r.append(thing)
        r += self.get_possessions()
        return r

    def get_gold(self):
        total = 0
        items = self.get_accessibles()
        for i in items:
            if i.name == 'Gold':
                total += i.durability
        return total

    def modify_gold(self, amount):
        items = self.get_accessibles()
        if amount > 0:
            for i in items:
                if i.name == 'Gold':
                    space = min(amount, 8 - i.durability)
                    i.durability += space
                    amount -= space
                if amount == 0:
                    return True
            if amount > 0:
                from src.entity.Stock import Stock
                Stock.make('Gold', self.pos).durability = amount
        elif amount < 0:
            amount = -amount
            if self.get_gold() >= amount:
                for i in items:
                    if i.name == 'Gold':
                        space = min(amount, i.durability)
                        i.durability -= space
                        amount -= space
                        if i.durability == 0:
                            i.die()
                    if amount == 0:
                        return True
