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

    def get_delay(self):
        return 4

    def get_cooldown(self):
        return 8

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
                    reachable = self.host.location.collide_land(self.host.pos, target.pos, self.host.sight,
                                                                distance=distance + 1, return_prev=False)
                    if target.pos == reachable:
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
                thing.pos.light_source = 0
                thing.pos.light = 0
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
    def get_delay(self):
        return 20

    def perform(self):
        if self.host == Global.player.character:
            ghost = Stock.make('Viewer', self.host.pos)
            Global.map_view.overlay.blackout()
            Global.map_view.overlay.colorize([25, 10, 125, 160])
            pos = Global.world.get_tile_true_pos(Global.player.character.pos.x, Global.player.character.pos.y)
            ghost.tags.set('tox', pos[0])
            ghost.tags.set('toy', pos[1])
            ghost.tags.set('view', 8)
            ghost.states.add('Script', self.get_power_0_4() * 8 + 16, '#reclaim')
            self.host.save = True
            Global.player.character.tags.set('husk', 1)
            Global.player.set_player(ghost)


class Passwall(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 100

    def perform(self):
        from src.map.Tile import Tile
        front = self.host.pos.get_cardinal(self.host.direction)
        if front.get_yield() == -10:
            self.host.move_line(front, flag=Tile.COLLIDE_MAGIC)


class Charm(Spell):
    def get_delay(self):
        return 8

    def get_cooldown(self):
        return 100

    def get_range(self):
        return 1

    def perform(self):
        target = self.auto_target(2)
        if target:
            from src.game.ScriptManual import ScriptManual
            ScriptManual.ally(Global.player.character, target)


class Transience(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 100

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
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 20

    def perform(self):
        target = self.cardinal_target(block=Tile.COLLIDE_ITEM)
        target.location.sound.register(target, 18, file='critical')
        Particle.make('disintegrate', target)
        if target.get_yield() == -10:
            target.set_terrain('.')
        else:
            for i in target.things.copy():
                i.decay(self.get_power_0_4() + 1)
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
                        Stock.make('Spell Wall', tile)


class Zombie(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 20

    def get_range(self):
        return self.get_power_0_9() + 3

    def perform(self):
        target = self.auto_target(0)
        if target:
            zombie_able = target.tags.get('zombie')
            if zombie_able:
                from src.tools.Data import Data
                zombie_type = Data.get_line('raw.txt', 'zombie')[1][zombie_able - 1]
                Particle.make('zwip', target.pos)
                target.location.sound.register(target.pos, 8, file='void')
                zombie = Stock.make(zombie_type, target.pos)
                health = target.tags.get('P', 1) + self.get_power_0_9()
                zombie.tags.set('P', health * 2)
                zombie.tags.set('p', health)
                from src.game.ScriptManual import ScriptManual
                ScriptManual.ally(Global.player.character, zombie)
                target.remove()


class Fog(Spell):
    def perform(self):
        self.host.location.sound.register(self.host.pos, 3, file='spell')
        length = self.get_power_0_4()
        for x in range(-length, length + 1):
            for y in range(-length, length + 1):
                tile = self.host.pos.get_neighbor(x, y)
                if tile and not tile.things:
                    fog = Stock.make('Fog', tile)
                    fog.states.add('Script', self.power + 40, 'remove')


class Find(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 100

    def perform(self):
        self.host.location.sound.register(self.host.pos, 3, file='spell')
        from src.tools.Data import Data
        armor = Global.r.rand_list(Data.get_line('raw.txt', 'find')[1][self.get_power_0_4()])
        Stock.make(armor, self.host.pos)


class Phantom(Spell):
    def get_range(self):
        return self.get_power_0_9() + 3

    def perform(self):
        target = self.auto_target(0)
        if target:
            target.location.sound.register(target.pos, 8, file='void')
            Particle.make('mist', target.pos)
            if isinstance(target, Item):
                if not target.host:
                    phantom = Stock.make('Phantom', target.pos)
                    phantom.set_host(target)
                    phantom.states.add('Script', self.power + 40, 'remove')
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
                summon.states.add('Script', self.get_power_0_4() * 2 + 16, 'remove')


class Gateway(Spell):
    def get_delay(self):
        return 24

    def get_cooldown(self):
        return 1200

    def perform(self):
        memory = Global.player.tags.remove('gateway')
        if memory:
            args = memory.split('&')
            portal = Stock.make('Gateway', self.host.pos)
            portal.states.add('Effect', -1, 'wind')
            portal.tags.set('tox', int(args[1]))
            portal.tags.set('toy', int(args[2]))
            portal.tags.set('#', 'travel')
        else:
            Stock.make('Gateway', self.host.pos)
            cell_coord = Global.world.get_tile_true_pos(self.host.pos.x, self.host.pos.y)
            memory = '&'.join([str(x) for x in [cell_coord[0], cell_coord[1]]])
            Global.player.tags.set('gateway', '&' + memory)
            self.host.location.sound.register(self.host.pos, 8, file='void')


class Transmogrify(Spell):
    def perform(self):
        target = self.auto_target(2)
        if target:
            target.location.sound.register(target.pos, 8, file='void')
            from src.entity.unit.Unit import Unit
            if isinstance(target, Unit):
                from src.tools.Data import Data
                pick = Data.get_line('raw.txt', 'transmogrify')[1]
                duration = self.get_power_0_9() * 40 + 40
                target.states.add('Shapeshift', duration, Global.r.rand_list(pick))


class Snare(Spell):
    def perform(self):
        for i in Spell.get_subjects(self.host.pos):
            if not i.states.get('Speed'):
                i.states.add('Speed', 40 * self.get_power_0_4() + 40, -20)
            return


class Fireball(Spell):
    def get_cooldown(self):
        return 20

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
        r.states.add('Script', 2, '>buff>*host>Burn>8>0')


class Arrow(Spell):
    def get_range(self):
        return self.get_power_0_9() + 1

    def perform(self):
        def fn(prev, tile):
            if tile:
                if not tile.is_seen():
                    return prev
                if tile.get_solidity() >= Tile.COLLIDE_FOG:
                    return tile
        destination = self.host.pos.get_cardinal(self.host.direction, distance=self.get_range())
        target = self.host.location.collide_line(self.host.pos.x, self.host.pos.y,
                                                 destination.x, destination.y, fn, 10)
        r = Stock.make('Arrow', self.host.pos)
        r.face(target.get_face(r.pos))
        r.relocate(to=target)
        self.host.location.field.register(1, target, delay=1)


class Bolt(Spell):
    def get_range(self):
        return self.get_power_0_9() + 1

    def perform(self):
        target = self.auto_target(2)
        if target:
            r = Stock.make('Arrow', self.host.pos)
            r.face(target.get_face(r.pos))
            r.relocate(to=target)
            self.host.location.field.register(1, target, delay=1)


class Blink(Spell):
    def perform(self):
        power = self.get_power_0_9() + 1
        x = Global.r.rand_int(-power, power)
        y = Global.r.rand_int(-power, power)
        destination = self.host.pos.get_neighbor(x, y)
        for i in self.host.pos.things:
            i.move_line(destination)


class Corona(Spell):
    def perform(self):
        radius = self.get_power_0_4() + 5
        duration = 40 + self.get_power_0_9() * 20
        for tile in self.host.pos.get_area(radius, radius):
            for thing in tile.things:
                Particle.make('shock', tile)
                thing.states.add('Glow', duration, 1)
                break


class Push(Spell):
    def get_delay(self):
        return 0

    def get_cooldown(self):
        return -80

    def perform(self):
        target = self.cardinal_target(block=Tile.COLLIDE_ITEM)
        Particle.make('wind', target)
        tile = target.get_cardinal(self.host.direction)
        for i in target.things.copy():
            i.relocate(to=tile)


class Jump(Spell):
    def get_delay(self):
        return 0

    def perform(self):
        power = self.get_power_0_4() + 2
        front = self.host.pos.get_cardinal(self.host.direction, distance=power)
        self.host.move_line(front, flag=self.host.collision_type + 2)


class Evacuate(Spell):
    def get_cooldown(self):
        return 200

    def perform(self):
        if self.host == Global.player.character:
            from src.tools.Data import Data
            pos = Global.r.rand_list(Data.get_line('raw.txt', 'evacuate')[1])
            Global.world.travel(pos[0], pos[1])
        else:
            self.host.location.sound.register(self.host.pos, 4, file='void')
            Particle.make('zwip', self.host.pos)
            self.host.remove()


class Torment(Spell):
    def get_delay(self):
        return 8

    def perform(self):
        targets = self.host.get_team(ally=False)
        power = self.get_power_0_9() + 1
        for i in targets:
            if (i.pos - self.host.pos).difference() <= power:
                self.host.location.sound.register(i.pos, 9, file='fire')
                if len(self.host.pos.things) < 5:
                    r = Stock.make('Flame', self.host.pos)
                    r.relocate(to=i.pos)
                    r.tags.set('p', power)
                    r.tags.set('P', power)


class Avatar(Spell):
    def perform(self):
        golem = Stock.make('Golem', self.host.pos)
        x = Global.r.rand_int(-1, 1)
        y = Global.r.rand_int(-1, 1)
        destination = self.host.pos.get_neighbor(x, y)
        golem.move_line(destination)
        golem.tags.set('team', self.host.tags.get('team', 0))
        golem.states.add('Script', 140 + self.power, 'remove')


class Summon(Spell):
    def get_delay(self):
        return 2

    def get_cooldown(self):
        return -80

    def get_range(self):
        return self.get_power_0_9() + 3

    def perform(self):
        target = self.auto_target(2)
        if target:
            power = 5 - self.get_power_0_4()
            x = Global.r.rand_int(-power, power)
            y = Global.r.rand_int(-power, power)
            destination = self.host.pos.get_neighbor(x, y)
            Particle.make('wind', target.pos)
            target.move_line(destination)
            target.states.add('Speed', 4, -10)
            target.location.sound.register(target.pos, 4, file='down')


class Barrier(Spell):
    def get_delay(self):
        return 14

    def perform(self):
        self.host.states.add('Barrier', 40 * self.get_power_0_4() + 40)


class Clone(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 600

    def get_range(self):
        return 1

    def perform(self):
        target = self.auto_target(0)
        if target:
            self.host.location.sound.register(self.host.pos, 0, file='void')
            Particle.make('barrier3', target.pos)
            from src.tools.Data import Data
            unit = Stock.get(target.location, target.name, data=Data.parse(target.__str__()))
            unit.add()
            x = Global.r.rand_int(-1, 1)
            y = Global.r.rand_int(-1, 1)
            destination = unit.pos.get_neighbor(x, y)
            unit.move_line(destination)
