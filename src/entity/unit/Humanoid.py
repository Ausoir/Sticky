from src.entity.unit.Inventory import Inventory
from src.entity.unit.Unit import Unit
from src.game import Global


class Humanoid(Unit):
    faces = []

    def __init__(self, location):
        super().__init__(location)
        self.inventory = Inventory(self)
        self.armor = None
        self.headgear = None
        self.weapon = None
        self.action.humanoid = True

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.armor else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.weapon else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear + ',' + self.inventory.__str__()

    def load(self, p):
        index = super().load(p)
        self.pilot.is_humanoid = True
        from src.entity.Stock import Stock
        if p[index]:
            if isinstance(p[index], str):
                armor = Stock.get(self.location, p[index])
            else:
                armor = Stock.get(self.location, p[index][2], p[index])
            armor.pos = self.pos
            armor.host = self
            armor.add()
            armor.wear(start=True)
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                headgear = Stock.get(self.location, p[index])
            else:
                headgear = Stock.get(self.location, p[index][2], p[index])
            headgear.pos = self.pos
            headgear.host = self
            headgear.add()
            headgear.wear(start=True)
        index += 1
        if p[index]:
            if isinstance(p[index], str):
                weapon = Stock.get(self.location, p[index])
            else:
                weapon = Stock.get(self.location, p[index][2], p[index])
            weapon.on_wield(self)
            weapon.add()
        index += 1
        self.inventory.load(p[index])
        return index + 1

    def update_tags(self):
        super().update_tags()
        self.form.organs[0].set(self.make_face())
        self.form.organs[0].form.show(True)

    def set_form(self, arg):
        self.form_name = arg
        from src.tools.Data import Data
        from src.form.BodyHumanoid import BodyHumanoid
        line = Data.get_line('model.txt', arg)
        self.form = BodyHumanoid(line[1], self)
        self.form.set_model(line[2])

    def show(self, visible):
        super().show(visible)
        if self.weapon:
            self.weapon.show(visible)
        if self.headgear:
            self.headgear.show(visible)

    def bound(self, visible):
        super().bound(visible)
        if self.weapon:
            self.weapon.bound(visible)
        if self.headgear:
            self.headgear.bound(visible)

    def get_hitter(self):
        if self.weapon:
            return self.weapon
        return self

    def get_damage(self):
        max_d = super().get_damage()
        if self.weapon:
            return max(self.weapon.tags.get('dmg', 0), max_d + self.weapon.tags.get('DMG', 0))
        else:
            return max_d

    def get_possessions(self):
        r = self.get_equipments()
        r += self.inventory.get_all_items()
        return r

    def get_equipments(self):
        r = []
        if self.weapon:
            r.append(self.weapon)
        if self.armor:
            r.append(self.armor)
        if self.headgear:
            r.append(self.headgear)
        return r

    def get_accessibles(self):
        r = super().get_accessibles()
        r += self.inventory.get_all_items()
        return r

    def get_skill(self, skill, stacks=False):
        r = super().get_skill(skill, stacks)
        if self.armor:
            if stacks or r == 0:
                if self.armor.tags.get('skill') == skill:
                    r += 1
        if self.headgear:
            if stacks or r == 0:
                if self.headgear.tags.get('skill') == skill:
                    r += 1
        return r

    def get_attack_motion(self):
        if not self.weapon:
            return 'kick'
        return super().get_attack_motion()

    def get_attack_speed(self):
        r = super().get_attack_speed()
        if self.weapon:
            r += self.weapon.tags.get('aspd', 0)
        return r

    def get_capacity(self):
        r = self.tags.get('space', 0)
        if self.armor:
            r += self.armor.tags.get('space', 0)
        if self.headgear:
            r += self.headgear.tags.get('space', 0)
        return r

    def get_equipment_weight(self):
        r = 0
        for i in self.get_possessions():
            r += i.get_weight()
        return r

    def get_weight(self):
        return super().get_weight() + self.get_equipment_weight()

    def is_vacant(self, weight):
        return self.get_capacity() >= self.get_equipment_weight() + weight

    def turn(self):
        super().turn()
        if self.weapon:
            self.weapon.turn()
        if self.headgear:
            self.headgear.turn()

    def use(self):
        if self.weapon:
            self.states.trigger(['act', 'use'])
            if not self.action.interact(self.weapon):
                self.weapon.use()
        else:
            self.action.attack()

    def relocate(self, to=None, x=None, y=None, force=False):
        super().relocate(to, x, y, force)
        if self.weapon:
            self.weapon.relocate(to=to, x=x, y=y, force=force)
        if self.armor:
            self.armor.relocate(to=to, x=x, y=y, force=force)
        if self.headgear:
            self.headgear.relocate(to=to, x=x, y=y, force=force)

    def remove(self):
        super().remove()
        if self.armor:
            self.armor.host = None
            self.armor.remove()
        if self.weapon:
            self.weapon.remove()
        if self.headgear:
            self.headgear.remove()

    def die(self):
        self.drop()
        self.inventory.drop_all()
        self.unarmor()
        self.unheadgear()
        super().die()

    def update(self):
        bound_x, bound_y = super().update()
        if self.weapon:
            if self.direction == 2:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 15
            elif self.direction == 0:
                x = bound_x + self.form.organs[3].lower_joint.x
                y = bound_y - self.form.organs[3].lower_joint.y
                arm = (self.form.organs[3].lower_joint - self.form.organs[3].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 30
            else:
                x = bound_x + self.form.organs[2].lower_joint.x
                y = bound_y - self.form.organs[2].lower_joint.y
                arm = (self.form.organs[2].lower_joint - self.form.organs[2].upper_joint).get_atan()
                self.weapon.form.rotation = arm - 90 + (15 * self.form.side)
            self.weapon.form.scale_x = self.form.side
            self.weapon.form.place(x, y)
        if self.headgear:
            x = bound_x + self.form.organs[0].lower_joint.x
            y = bound_y - self.form.organs[0].lower_joint.y
            neck = (self.form.organs[0].lower_joint - self.form.organs[0].upper_joint).get_atan()
            self.headgear.form.rotation = neck + 90
            self.headgear.form.place(x, y)
        return bound_x, bound_y

    def face(self, direction):
        if self.headgear:
            self.headgear.face(direction)
        return super().face(direction)

    def hit(self, damage, hitter=None):
        r = 0
        if self.calculate_hit(damage, hitter):
            if self.armor and Global.r.rand_float() * 100 < self.armor.tags.get('cov', 0):
                self.display_hp()
            else:
                r = super().hit(damage, hitter)
        return r

    def get_durability(self):
        hp = self.tags.get('p')
        mhp = self.tags.get('P')
        if self.armor:
            a_hp = self.armor.tags.get('p')
            a_mhp = self.armor.tags.get('P')
        else:
            a_hp = 0
            a_mhp = 0
        return a_hp, a_mhp, hp, mhp

    def display_hp(self):
        a_hp, a_mhp, hp, mhp = self.get_durability()
        if a_mhp > 0:
            self.healthbar.colorize(a_hp / a_mhp)
        else:
            self.healthbar.colorize(0)
        if mhp > 0:
            self.healthbar.appear(hp, mhp)

    def on_attack(self, target):
        super().on_attack(target)
        if self.weapon:
            self.weapon.on_attack(target)
        else:
            if isinstance(target, Humanoid):
                if self.get_skill('steal'):
                    concentration = self.states.get('Concentration')
                    if concentration:
                        concentration.trigger(['spend'])
                        weapon = target.drop()
                        if weapon:
                            self.pick_up(weapon)
                    else:
                        self.location.sound.register(self.pos, 0, file='wear', priority=2)
                        item = target.inventory.take_item(0)
                        if item:
                            self.pick_up(item)

    def drop(self):
        if self.weapon:
            r = self.weapon
            self.weapon.on_unwield()
            self.weapon = None
            return r

    def unarmor(self):
        if self.armor:
            return self.armor.unwear()

    def unheadgear(self):
        if self.headgear:
            return self.headgear.unwear()

    def make_face(self):
        from src.form.Picture import Model
        face = Humanoid.faces[self.get_seed() % len(Humanoid.faces)]
        model = Model(face)
        return model

    def unsheathe(self, index):
        item = self.inventory.take_item(index)
        if item:
            def change():
                self.drop()
                item.on_wield(self)
            self.action.act('grab', 8)
            self.action.on_finish = change
            self.action.delay = 4

    def pick_up(self, item):
        if self.weapon:
            self.inventory.attempt_add(item)
        else:
            if self.is_vacant(item.get_weight()):
                item.on_wield(self)
            else:
                from src.tools.Dialog import Dialog
                params = [self.get_equipment_weight(), self.get_capacity(), item.get_weight()]
                if self == Global.player.character:
                    Global.main.monologue.set(Dialog.get('!heavy', params))

    def on_sleep(self, time):
        super().on_sleep(time)
        if self.weapon:
            self.weapon.on_sleep(time)
        if self.armor:
            self.armor.on_sleep(time)
        if self.headgear:
            self.headgear.on_sleep(time)
