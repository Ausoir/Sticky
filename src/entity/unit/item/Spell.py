from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.item.Item import Item
from src.game import Global
from src.map.Tile import Tile


class Spell:
    @staticmethod
    def get(spell, power=0):
        for i in Spell.__subclasses__():
            if i.__name__ == spell.title():
                r = i()
                r.set_power(power)
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
        self.power = 0

    def set_power(self, power):
        self.power = max(0, min(100, power))

    def get_power_0_3(self):
        return int(self.power / 33)

    def get_power_0_4(self):
        return int(self.power / 25)

    def get_power_0_9(self):
        return int(self.power / 10)

    def get_range(self):
        return 13

    def cast(self, host, motion='cast', delay=4):
        self.host = host
        host.action.act(motion, time=delay)
        host.action.on_finish = self.perform

    def cast_on(self, host):
        self.host = host
        self.perform()

    def perform(self):
        pass

    def auto_target(self, team):
        if team == 0:
            targets = self.host.location.population.get_all()
        elif team == 1:
            targets = self.host.get_team(ally=True)
        else:
            targets = self.host.get_team(ally=False)
        nearest = None
        nearest_dist = self.get_range() + 1
        for target in targets:
            if target.pos != self.host.pos and self.host.direction == self.host.pos.get_face(target.pos):
                distance = (target.pos - self.host.pos).difference()
                if distance < nearest_dist:
                    nearest_dist = distance
                    nearest = target
        return nearest

    def cardinal_target(self, block=Tile.COLLIDE_OBJECT):
        direction = self.host.direction
        start = self.host.pos
        max_range = self.get_range()
        destination = self.host.pos.get_cardinal(direction, distance=max_range)
        target = self.host.location.collide_land(start, destination, block, distance=max_range, return_prev=False)
        return target


class Dispel(Spell):
    def perform(self):
        self.host.location.sound.register(self.host.pos, 0, file='energy')
        targets = self.host.pos.get_area(self.get_power_0_9(), self.get_power_0_9())
        for i in targets:
            Particle.make('sonic', i)
            for thing in i.things.copy():
                thing.hit(0)
                thing.states.clear(lambda x: 'magic' in x.get_tags())


class Glow(Spell):
    def get_range(self):
        return self.get_power_0_9()

    def perform(self):
        target = self.auto_target(0)
        if target:
            Particle.make('shock', target.pos)
            if self.get_power_0_9() >= 9:
                duration = -1
            else:
                duration = 40 + self.get_power_0_9() * 120
            target.states.add('Glow', duration, self.get_power_0_9() + 1)


class Scorch(Spell):
    def get_range(self):
        return self.get_power_0_9() + 1

    def perform(self):
        target = self.auto_target(0)
        if target:
            self.host.location.sound.register(target.pos, 9, file='fire')
            r = Stock.make('Flame', self.host.pos)
            r.relocate(to=target.pos)
            r.tags.set('p', self.get_power_0_9())
            r.tags.set('P', self.get_power_0_9())


class Scry(Spell):
    def perform(self):
        if self.host == Global.player.character:
            ghost = Stock.make('Ghost', self.host.pos)
            ghost.tags.set('team', self.host.tags.get('team', 0))
            ghost.states.add('Invisibility', -1, 0)
            pos = Global.world.get_tile_true_pos(Global.player.character.pos.x, Global.player.character.pos.y)
            ghost.tags.set('spd', 10)
            ghost.tags.set('tox', pos[0])
            ghost.tags.set('toy', pos[1])
            ghost.states.add('Script', 160, '#reclaim')
            self.host.save = True
            Global.player.set_player(ghost)


class Passwall(Spell):
    def perform(self):
        from src.map.Tile import Tile
        front = self.host.pos.get_cardinal(self.host.direction)
        if front.get_yield() == -10:
            self.host.move_line(front, flag=[Tile.COLLIDE_MAGIC])


class Charm(Spell):
    def perform(self):
        for i in self.auto_target(2):
            i.tags.set('team', self.host.tags.get('team', 0))
            i.pilot.load('ally')


class Transience(Spell):
    def perform(self):
        ghost = Stock.make('Ghost', self.host.pos)
        ghost.tags.set('team', self.host.tags.get('team', 0))
        if self.host == Global.player.character:
            self.host.save = True
            Global.player.set_player(ghost)
        else:
            self.host.tags.remove('ai')
        return


class Disintegration(Spell):
    def perform(self):
        target = self.cardinal_target(block=Tile.COLLIDE_ITEM)
        target.location.sound.register(target, 18, file='critical')
        Particle.make('disintegrate', target)
        if target.get_yield() == -10:
            target.set_terrain('.')
        else:
            for i in target.things.copy():
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
                    tile = self.host.pos.get_neighbor(x, y)
                    if tile and not tile.things:
                        r = Stock.make('Spell Wall', tile)
                        r.states.add('Script', duration, 'remove')


class Zombie(Spell):
    def perform(self):
        target = self.auto_target(0)
        if target:
            from src.entity.Other import Corpse
            if isinstance(target, Corpse):
                Particle.make('zwip', target)
                target.location.sound.register(target, 8, file='void')
                zombie = Stock.make('Zombie', target.pos)
                health = target.tags.get('P', 1) + self.get_power_0_9()
                zombie.tags.set('P', health * 2)
                zombie.tags.set('p', health)
                zombie.tags.set('team', self.host.tags.get('team', 0))
                target.remove()


class Fog(Spell):
    def perform(self):
        self.host.location.sound.register(self.host.pos, 3, file='spell')
        length = self.get_power_0_4()
        for x in range(-length, length + 1):
            for y in range(-length, length + 1):
                tile = self.host.pos.get_neighbor(x, y)
                if tile and not tile.things:
                    Stock.make('Fog', tile)


class Find(Spell):
    def perform(self):
        self.host.location.sound.register(self.host.pos, 3, file='spell')
        from src.tools.Data import Data
        armor = Global.r.rand_list(Data.get_line('raw.txt', 'find')[1][self.get_power_0_4()])
        Stock.make(armor, self.host.pos)


class Phantom(Spell):
    def perform(self):
        target = self.auto_target(0)
        if target:
            target.location.sound.register(target.pos, 8, file='void')
            Particle.make('mist', target.pos)
            if isinstance(target, Item):
                if not target.host:
                    phantom = Stock.make('Phantom', target.pos)
                    phantom.set_host(target)
                    phantom.states.add('Script', self.power * 160 + 160, 'remove')
                    phantom.tags.set('team', self.host.tags.get('team', 0))
                    return


class Pester(Spell):
    def perform(self):
        target = self.auto_target(2)
        if target:
            target.location.sound.register(target.pos, 8, file='void')
            for i in range(self.get_power_0_3() + 1):
                space = target.pos.get_neighbor(Global.r.rand_int(-3, 3), Global.r.rand_int(-3, 3))
                summon = Stock.make('Moth', space)
                Particle.make('zwip', space)
                summon.tags.set('team', self.host.tags.get('team', 0))
                summon.tags.set('task', 'Attack')
                summon.pilot.retarget('x' + str(target.pos.x) + 'y' + str(target.pos.y))
                summon.states.add('Script', self.get_power_0_9() + 8, 'remove')


class Locate(Spell):
    def perform(self):
        summon = Stock.make('Mark', self.host.pos)
        summon.tags.set('data', self.host.pos)


class Gateway(Spell):
    def perform(self):
        summon = Stock.make('Gateway', self.host.pos)
        summon.tags.set('power', self.power)


class Slime(Spell):
    def perform(self):
        target = self.auto_target(2)
        if target:
            from src.game.ScriptManual import ScriptManual
            ScriptManual.shapeshift(target, 'Slime')


class Dog(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.host.pos):
            from src.game.ScriptManual import ScriptManual
            ScriptManual.shapeshift(i, 'Dog')
            return


class Transmogrify(Spell):
    def perform(self):
        target = self.auto_target(2)
        if target:
            target.location.sound.register(target.pos, 8, file='void')
            from src.entity.unit.Unit import Unit
            if isinstance(target, Unit):
                from src.tools.Data import Data
                from src.game.ScriptManual import ScriptManual
                pick = Data.get_line('raw.txt', 'transmogrify')[1]
                duration = self.get_power_0_9() * 40 + 40
                target.states.add('Shapeshift', duration, Global.r.rand_list(pick))


class Slow(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.host.pos):
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
        if self.host:
            origin = self.host.pos
        else:
            origin = self.host.pos
        r = Stock.make('Fireball', origin)
        r.tags.increment('fuel', self.get_power_0_4())
        destination = self.host.pos.get_cardinal(self.host.direction, distance=self.get_range())
        self.host.location.sound.register(destination, 9, file='fire')
        r.relocate(to=destination)
        r.states.add('Script', 2, '>buff>Burn>8>0')


class Arrow(Spell):
    def get_range(self):
        return self.get_power_0_9() + 1

    def perform(self):
        def fn(prev, tile):
            if tile:
                if not tile.in_sight:
                    return prev
                if tile.get_solidity() >= Tile.COLLIDE_FOG:
                    return tile
        destination = self.host.pos.get_cardinal(self.host.direction, distance=self.get_range())
        target = self.host.location.collide_line(self.host.pos.x, self.host.pos.y,
                                                destination.x, destination.y, fn, 10)
        r = Stock.make('Arrow', self.host.pos)
        r.face(target.get_face(r.pos))
        r.relocate(to=target)
        self.host.location.field.register(40, target, delay=1)


class Blink(Spell):
    def perform(self):
        power = self.get_power_0_9()
        x = Global.r.rand_int(-power, power)
        y = Global.r.rand_int(-power, power)
        for i in self.host.pos.things:
            i.relocate(to=self.host.pos.get_neighbor(x, y))


class Banish(Spell):
    def perform(self):
        self.host.location.sound.register(self.host.pos, 4, file='void')
        Particle.make('zwip', self.host.pos)
        for i in self.host.pos.things:
            i.remove()


class Corona(Spell):
    def perform(self):
        radius = self.get_power_0_4() + 5
        duration = 40 + self.get_power_0_9() * 20
        for tile in self.host.pos.get_area(radius, radius):
            for thing in tile.things:
                Particle.make('shock', tile)
                thing.states.add('Glow', duration, 1)
                break
