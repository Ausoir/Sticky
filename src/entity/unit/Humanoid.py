from src.entity.unit.Unit import Unit
from src.game import Global


class Humanoid(Unit):
    faces = []

    def __init__(self, location):
        super().__init__(location)
        self.armor = None
        self.headgear = None
        self.weapon = None
        self.action.humanoid = True

    def __str__(self):
        armor = '['+self.armor.__str__()+']' if self.armor else '0'
        headgear = '['+self.headgear.__str__()+']' if self.headgear else '0'
        weapon = '['+self.weapon.__str__()+']' if self.weapon else '0'
        gear = armor + ',' + headgear + ',' + weapon
        return super().__str__() + ',' + gear

    def load(self, p):
        index = super().load(p)
        self.pilot.is_humanoid = True
        e_weapon = self.tags.remove('e_weapon')
        e_armor = self.tags.remove('e_armor')
        e_head = self.tags.remove('e_head')
        from src.entity.Stock import Stock
        from src.tools.Data import Data
        if e_armor:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_armor)[1])
        if p[index]:
            if isinstance(p[index], str):
                start = False
                armor = Stock.get(self.location, p[index])
            else:
                start = True
                armor = Stock.get(self.location, p[index][2], p[index])
            armor.host = self
            armor.wear(start=start)
        index += 1
        if e_head:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_head)[1])
        if p[index]:
            if isinstance(p[index], str):
                start = False
                headgear = Stock.get(self.location, p[index])
            else:
                start = True
                headgear = Stock.get(self.location, p[index][2], p[index])
            headgear.host = self
            headgear.wear(start=start)
        index += 1
        if e_weapon:
            p[index] = Global.r.rand_list(Data.get_line('habitat.txt', e_weapon)[1])
        if p[index]:
            if isinstance(p[index], str):
                start = False
                weapon = Stock.get(self.location, p[index])
            else:
                start = True
                weapon = Stock.get(self.location, p[index][2], p[index])
            weapon.on_wield(self, start=start)
        return index + 1

    def add(self):
        r = super().add()
        if r:
            if self.armor:
                self.armor.pos = self.pos
                self.armor.add()
            if self.headgear:
                self.headgear.pos = self.pos
                self.headgear.add()
            if self.weapon:
                self.weapon.pos = self.pos
                self.weapon.add()
            return r

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

    def get_skills(self):
        r = super().get_skills()
        if self.weapon and self.weapon.tags.get('skill'):
            r.append(self.weapon.tags.get('skill'))
        if self.armor and self.armor.tags.get('skill'):
            r.append(self.armor.tags.get('skill'))
        if self.headgear and self.headgear.tags.get('skill'):
            r.append(self.headgear.tags.get('skill'))
        return r

    def get_skill(self, skill):
        r = super().get_skill(skill)
        if self.weapon and self.weapon.tags.get('skill') == skill:
            r += 1
        if self.armor and self.armor.tags.get('skill') == skill:
            r += 1
        if self.headgear and self.headgear.tags.get('skill') == skill:
            r += 1
        return r

    def get_equipment_weight(self):
        r = 0
        for i in self.get_possessions():
            r += i.get_weight()
        return r

    def get_weight(self):
        return super().get_weight() + self.get_equipment_weight()

    def is_vacant(self, weight):
        return self.tags.get('str', 1) >= self.get_equipment_weight() + weight

    def turn(self):
        super().turn()
        if self.tags.get('p', 0) == 1:
            from src.entity.Particle import Particle
            Particle.make('blood', self.pos, offset=8)

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

    def deregister(self):
        super().deregister()
        if self.weapon:
            self.weapon.deregister()
        if self.armor:
            self.armor.deregister()
        if self.headgear:
            self.headgear.deregister()

    def remove(self):
        if super().remove():
            if self.armor:
                self.armor.host = None
                self.armor.remove()
            if self.weapon:
                self.weapon.remove()
            if self.headgear:
                self.headgear.remove()
            return True

    def die(self):
        self.drop()
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

    def get_durability(self):
        hp = self.tags.get('p', 0)
        mhp = self.tags.get('P', 0)
        if self.armor:
            a_hp = self.armor.tags.get('p') or 0
            a_mhp = self.armor.tags.get('P') or 0
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
        heads = self.tags.get('head')
        if heads:
            heads = heads.split('&')
            face = []
            from src.tools.Data import Data
            for image in heads:
                face.append(Data.get_cache(image))
        else:
            face = Humanoid.faces[self.get_seed() % len(Humanoid.faces)]
        from src.form.Picture import Model
        model = Model(face)
        return model

    def unsheathe(self, index):
        item = self.inventory.take_item(index)
        if item:
            def change():
                self.drop()
                item.on_wield(self)
            self.action.act('grab', 4)
            self.action.on_finish = change
            self.action.delay = 4
            return item

    def pick_up(self, item):
        item.relocate(to=self.pos)
        if self.weapon:
            self.inventory.attempt_add(item)
        else:
            if self.is_vacant(item.get_weight()):
                item.on_wield(self)
            else:
                from src.tools.Dialog import Dialog
                params = [self.get_equipment_weight(), self.tags.get('str', 1), item.get_weight()]
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
