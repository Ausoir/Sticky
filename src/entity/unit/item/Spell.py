from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.Unit import Unit
from src.entity.unit.item.Item import Item
from src.game import Global
from src.map.Tile import Tile


class Spell:
    @staticmethod
    def get(spell, power=0, on_self=False):
        for i in Spell.__subclasses__():
            if i.__name__ == spell.title():
                r = i()
                r.set_power(power)
                r.on_self = on_self
                return r

    @staticmethod
    def get_subjects(pos):
        units = []
        props = []
        from src.entity.unit.Unit import Unit
        for i in pos.things:
            if isinstance(i, Unit):
                units.append(i)
            else:
                props.append(i)
        return units + props

    def __init__(self):
        self.host = None
        self.pos = None
        self.power = 0
        self.on_self = False

    def set_power(self, power):
        self.power = max(0, min(100, power))

    def get_power_0_4(self):
        return int(self.power / 20)

    def get_power_0_9(self):
        return int(self.power / 10)

    def get_range(self):
        return 13

    def cast(self, host, motion='cast', delay=4):
        self.host = host
        if not self.on_self and host.target:
            host.face_toward(host.target)
        host.action.act(motion, time=delay)
        host.action.on_finish = self.on_cast

    def cast_on(self, pos):
        self.pos = pos
        self.perform()

    def on_cast(self):
        if not self.on_self and self.host.target:
            self.pos = self.host.target
        else:
            self.pos = self.host.pos
        self.perform()

    def perform(self):
        pass

    def beam_target(self, block=Tile.COLLIDE_OBJECT, max_range=13):
        if self.host:
            start = self.host.pos
        else:
            start = self.pos
        target = self.pos.location.collide_land(start, self.pos, block, distance=max_range)
        return target

    def cardinal_target(self, block=Tile.COLLIDE_OBJECT, max_range=13):
        if self.host:
            direction = self.host.direction
            start = self.host.pos
        else:
            direction = Global.r.rand_int(1, 4)
            start = self.pos
        destination = self.pos.get_cardinal(direction, distance=max_range)
        target = self.pos.location.collide_land(start, destination, block, distance=max_range, return_prev=False)
        return target


class Dispel(Spell):
    def perform(self):
        self.pos.location.sound.register(self.pos, 0, file='energy')
        targets = self.pos.get_area(self.get_power_0_9(), self.get_power_0_9())
        for i in targets:
            Particle.make('sonic', i)
            for thing in i.things.copy():
                thing.hit(0)
                thing.states.clear(lambda x: 'magic' in x.get_tags())


class Glow(Spell):
    def get_range(self):
        return self.get_power_0_9()

    def perform(self):
        target = self.beam_target(max_range=self.get_range())
        Particle.make('shock', target)
        if self.get_power_0_9() >= 9:
            duration = -1
        else:
            duration = 40 + self.get_power_0_9() * 10
        for i in Spell.get_subjects(target):
            i.states.add('Glow', duration, self.get_power_0_9())


class Scorch(Spell):
    def get_range(self):
        return self.get_power_0_9()

    def perform(self):
        target = self.beam_target(max_range=self.get_range())
        self.pos.location.sound.register(target, 9, file='fire')
        r = Stock.make('Flame', self.host.pos)
        r.relocate(to=target)
        r.tags.set('p', self.get_power_0_9())
        r.tags.set('P', self.get_power_0_9())


class Scry(Spell):
    def perform(self):
        if self.pos == Global.player.character.pos:
            def effect():
                to = r.pos.get_cardinal(Global.player.character.direction)
                r.move_line(to, flag=[Tile.COLLIDE_MAGIC])
                if turnee.lifetime == 0:
                    Global.map_view.overlay.weather = orig[0]
                    Global.map_view.set_sight_range(orig[1])
                    Global.map_view.set_view_range(orig[2])
                    Global.map_view.on_sight_change()
                    Global.player.character.center_camera()
                    r.remove()
                Particle.make('sonic', r.pos)
            Global.player.character.states.add('Speed', 60, var=-12)
            from src.map.Tile import Tile
            from src.tools.Turnee import Turnee
            orig = [Global.map_view.overlay.weather, Global.map_view.sight_range, Global.map_view.view_range]
            Global.map_view.overlay.weather = [45, 25, 75, 160]
            Global.map_view.set_sight_range(13)
            Global.map_view.set_view_range(13)
            Global.map_view.on_sight_change()
            turnee = Turnee(effect, 10 * self.get_power_0_9())
            r = Stock.make('Force', self.pos)
            r.center_camera()


class Vision(Spell):
    def perform(self):
        for i in self.pos.things:
            if isinstance(i, Unit):
                i.states.add('Vision', -1)


class Passwall(Spell):
    def perform(self):
        for i in self.pos.things:
            if isinstance(i, Unit):
                from src.map.Tile import Tile
                front = i.pos.get_cardinal(i.direction)
                if front.get_yield() == -10:
                    i.move_line(front, flag=[Tile.COLLIDE_MAGIC])
                    return


class Restoration(Spell):
    def get_range(self):
        return self.get_power_0_9()

    def perform(self):
        target = self.beam_target(max_range=self.get_range())
        Particle.make('heal', target)
        for i in Spell.get_subjects(target):
            i.states.add('Health', 10 * self.get_power_0_9(), 1)
            if isinstance(i, Unit):
                if i.pilot.priority > 1:
                    from src.entity.unit.Actions import Actions
                    Actions.knockdown(i, 10 * self.get_power_0_9())
            return


class Haste(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            if isinstance(i, Item) and i.enhance(Global.r.rand_int(1, self.power)):
                i.tags.increment('aspd', 1)
            elif not i.states.get('Speed'):
                i.states.add('Speed', 40 * self.get_power_0_4(), 2)
                i.states.add('Fatigue', 40 * self.get_power_0_4(), 2)
            return


class Levitation(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            i.states.add('Levitation', -1)
            if self.power == 100 and isinstance(i, Item):
                w = i.tags.get('w')
                if w > 1:
                    if i.enhance(Global.r.rand_int(1, self.power)):
                        i.tags.increment('w', -1)
            return


class Invisibility(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            i.states.add('Invisible', -1)
            return


class Charm(Spell):
    def perform(self):
        for i in self.pos.things:
            if i.tags.get('team', -1) != -1:
                i.tags.set('team', 0)
                i.pilot.load('ally')


class Transience(Spell):
    def perform(self):
        from src.entity.unit.Unit import Unit
        for i in self.pos.things:
            if isinstance(i, Unit):
                ghost = Stock.make('Ghost', self.pos)
                ghost.set_team(i)
                if i == Global.player.character:
                    i.save = True
                    Global.player.set_player(ghost)
                else:
                    i.tags.remove('ai')
                return


class Lignify(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            if isinstance(i, Item):
                from src.entity.unit.item.Focus import Focus
                if isinstance(i, Focus):
                    i.catalyst = 'Wand'
                    i.set_form('g_20x4')
                    i.show(True)
                elif i.enhance(Global.r.rand_int(1, self.power)):
                    i.tags.increment('DEF', 1)
                else:
                    Stock.make('Stick', self.pos)
                    i.remove()
            else:
                i.states.add('Lignification', -1)
            return


class Petrify(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            if isinstance(i, Item):
                if i.enhance(Global.r.rand_int(1, self.power)):
                    i.tags.increment('def', 1)
                    i.tags.increment('w', 1)
                else:
                    Stock.make('Chalk', self.pos)
                    i.remove()
            else:
                i.states.add('Petrification', -1)
            return


class Disintegration(Spell):
    def perform(self):
        self.pos.location.sound.register(self.pos, 18, file='critical')
        Particle.make('disintegrate', self.pos)
        if self.pos.get_yield() == -10:
            self.pos.set_terrain('.')
        else:
            for i in self.pos.things.copy():
                i.decay(self.get_power_0_9() * 5)
                if i.name == 'Corpse':
                    Stock.make('Raw Meat', i.pos)


class Wall(Spell):
    def perform(self):
        if self.power == 100:
            duration = -1
        else:
            duration = self.get_power_0_9() * 40
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    tile = self.pos.get_neighbor(x, y)
                    if tile and not tile.things:
                        r = Stock.make('Spell Wall', tile)
                        r.states.add('Script', duration, 'remove')


class Zombie(Spell):
    def perform(self):
        from src.entity.Other import Corpse
        self.pos.location.sound.register(self.pos, 8, file='void')
        Particle.make('zwip', self.pos)
        for i in self.pos.things.copy():
            if isinstance(i, Corpse) or i.name == 'Raw Meat':
                zombie = Stock.make('Zombie', i.pos)
                health = i.tags.get('P', 1) + self.get_power_0_9()
                zombie.tags.set('P', health * 2)
                zombie.tags.set('p', health)
                i.remove()
                return


class Fog(Spell):
    def perform(self):
        self.pos.location.sound.register(self.pos, 3, file='spell')
        length = self.get_power_0_4()
        for x in range(-length, length + 1):
            for y in range(-length, length + 1):
                tile = self.pos.get_neighbor(x, y)
                if tile and not tile.things:
                    Stock.make('Fog', tile)


class Find(Spell):
    def perform(self):
        self.pos.location.sound.register(self.pos, 3, file='spell')
        from src.tools.Data import Data
        armor = Global.r.rand_list(Data.get_line('raw.txt', 'find')[1][self.get_power_0_4()])
        Stock.make(armor, self.pos)


class Phantom(Spell):
    def perform(self):
        self.pos.location.sound.register(self.pos, 8, file='void')
        Particle.make('mist', self.pos)
        for i in self.pos.things.copy():
            if isinstance(i, Item):
                phantom = Stock.make('Phantom', self.pos)
                phantom.set_host(i)
                phantom.states.add('Script', self.power * 40, 'remove')
                return


class Locate(Spell):
    def perform(self):
        summon = Stock.make('Mark', self.pos)
        summon.tags.set('data', self.pos)


class Gateway(Spell):
    def perform(self):
        summon = Stock.make('Gateway', self.pos)
        summon.tags.set('power', self.power)


class Slime(Spell):
    def perform(self):
        from src.entity.unit.item.Focus import Focus
        for i in Spell.get_subjects(self.pos):
            if isinstance(i, Focus):
                i.catalyst = 'Potion'
                i.set_form('g_10x4')
                i.show(True)
            else:
                from src.game.ScriptManual import ScriptManual
                ScriptManual.shapeshift(i, 'Slime')
            return


class Dog(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            from src.game.ScriptManual import ScriptManual
            ScriptManual.shapeshift(i, 'Dog')
            return


class Man(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            from src.game.ScriptManual import ScriptManual
            ScriptManual.shapeshift(i, 'Human')
            return


class Slow(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.pos):
            if isinstance(i, Item) and i.enhance(Global.r.rand_int(1, self.power)):
                i.tags.increment('aspd', -1)
            elif not i.states.get('Speed'):
                i.states.add('Speed', 40 * self.get_power_0_4(), -2)
                i.states.add('Fatigue', 40 * self.get_power_0_4(), -2)
            return


class Fireball(Spell):
    def get_range(self):
        return self.get_power_0_4() + 3

    def perform(self):
        target = self.beam_target(max_range=self.get_range())
        self.pos.location.sound.register(target, 9, file='fire')
        r = Stock.make('Fireball', self.host.pos)
        r.tags.increment('fuel', self.get_power_0_4())
        r.relocate(to=target)
        r.states.add('Script', 2, '>buff>Burn>8>0')


class Arrow(Spell):
    def get_range(self):
        return self.get_power_0_9() + 1

    def perform(self):
        target = self.cardinal_target(max_range=self.get_range(), block=Tile.COLLIDE_FOG)
        # self.pos.location.sound.register(target, 3, file='rip')
        r = Stock.make('Arrow', self.host.pos)
        r.face(target.get_face(r.pos))
        r.relocate(to=target)
        self.host.location.field.register(40, target, delay=1)
