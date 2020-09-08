from src.entity.Particle import Particle
from src.entity.Stock import Stock
from src.entity.unit.item.Item import Item
from src.game import Global
from src.map.Tile import Tile


class Spell:
    @staticmethod
    def get(spell):
        for i in Spell.__subclasses__():
            if i.__name__ == spell.title():
                r = i()
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

    def get_delay(self):
        return 4

    def get_cooldown(self):
        return 100

    def get_range(self):
        return 13

    def get_motion(self):
        return 'cast'

    def cast(self, host, motion=None, delay=None):
        self.host = host
        if not motion:
            motion = self.get_motion()
        if not delay:
            delay = self.get_delay()
        if delay == 0:
            self.perform()
        else:
            host.action.act(motion, delay)
            host.action.on_finish = self.perform

    def cast_on(self, host):
        self.host = host
        self.perform()

    def perform(self):
        pass

    def auto_target(self, team):
        if team == 0:
            targets = Global.world.location.population.get_all()
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
                    reachable = Global.world.location.collide_land(self.host.pos, target.pos, self.host.sight,
                                                                   distance=distance + 1, prev=False)
                    if target.pos == reachable:
                        nearest_dist = distance
                        nearest = target
        return nearest

    def cardinal_target(self, block=Tile.COLLIDE_OBJECT):
        direction = self.host.direction
        start = self.host.pos
        max_range = self.get_range()
        destination = self.host.pos.get_cardinal(direction, distance=max_range)
        target = Global.world.location.collide_land(start, destination, block, distance=max_range, prev=False)
        return target


class Dispel(Spell):
    def perform(self):
        Global.world.location.sound.register(self.host.pos, 0, file='energy')
        targets = self.host.pos.get_area(9, 9)
        for i in targets:
            dispelled = False
            for thing in i.things.copy():
                dispelled = True
                thing.hit(0)
                thing.pos.light_source = 0
                thing.pos.light = 0
                thing.states.clear(lambda x: 'magic' in x.get_tags())
            if dispelled:
                Particle.make('sonic', i)


class Glow(Spell):
    def get_range(self):
        return 9

    def perform(self):
        target = self.auto_target(0)
        if target:
            Particle.make('shock', target.pos)
            glow = target.states.get('Glow')
            if glow:
                target.states.add('Glow', -1, min(12, glow.var + 4))
            target.states.add('Glow', -1, 5)


class Scorch(Spell):
    def get_range(self):
        return 9

    def perform(self):
        target = self.auto_target(0)
        if target:
            Global.world.location.sound.register(target.pos, 9, file='fire')
            r = Stock.make('Flame', self.host.pos)
            r.relocate(to=target.pos)


class Scry(Spell):
    def get_delay(self):
        return 20

    def perform(self):
        if self.host == Global.player.character:
            ghost = Stock.make('Viewer', self.host.pos)
            pos = Global.world.get_tile_true_pos(Global.player.character.pos.x, Global.player.character.pos.y)
            ghost.tags.set('tox', pos[0])
            ghost.tags.set('toy', pos[1])
            ghost.tags.set('view', 8)
            ghost.states.add('Script', 80, '#reclaim')
            self.host.is_save = True
            Global.player.character.tags.set('husk', 1)
            Global.player.set_player(ghost)
            Global.map_view.overlay.blackout()
            Global.map_view.overlay.colorize([25, 10, 125, 160])


class Passwall(Spell):
    def get_delay(self):
        return 14

    def perform(self):
        from src.map.Tile import Tile
        front = self.host.pos.get_cardinal(self.host.direction)
        if front.get_yield() == -10:
            self.host.move_line(front, flag=Tile.COLLIDE_MAGIC)


class Charm(Spell):
    def get_delay(self):
        return 8

    def get_range(self):
        return 1

    def perform(self):
        target = self.auto_target(2)
        if target:
            from src.game.ScriptManual import ScriptManual
            ScriptManual.ally(self.host, target)


class Transience(Spell):
    def get_delay(self):
        return 14

    def perform(self):
        ghost = Stock.make('Ghost', self.host.pos)
        ghost.tags.set('team', self.host.tags.get('team', 0))
        Global.world.location.population.adjust(ghost)
        if self.host == Global.player.character:
            self.host.is_save = True
            Global.player.set_player(ghost)
        else:
            self.host.tags.remove('ai')
        return


class Disintegrate(Spell):
    def get_delay(self):
        return 14

    def perform(self):
        target = self.cardinal_target(block=Tile.COLLIDE_ITEM)
        Global.world.location.sound.register(target, 18, file='critical')
        Particle.make('disintegrate', target)
        if target.get_yield() == -10:
            self.host.action.crush()
        else:
            for i in target.things.copy():
                i.decay(8)
                if i.name == 'Corpse':
                    Stock.make('Raw Meat', i.pos)


class Wall(Spell):
    def perform(self):
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x != 0 or y != 0:
                    tile = self.host.pos.get_neighbor(x, y)
                    if tile and not tile.things:
                        Stock.make('Spell Wall', tile)


class Reanimate(Spell):
    def get_delay(self):
        return 14

    def get_range(self):
        return 9

    def perform(self):
        target = self.auto_target(0)
        if target:
            zombie_able = target.tags.get('zombie')
            if zombie_able:
                from src.tools.Data import Data
                zombie_type = Data.get_line('raw.txt', 'zombie')[1][zombie_able - 1]
                Particle.make('zwip', target.pos)
                Global.world.location.sound.register(target.pos, 8, file='void')
                zombie = Stock.make(zombie_type, target.pos)
                from src.game.ScriptManual import ScriptManual
                ScriptManual.ally(self.host, zombie)
                target.remove()


class Fog(Spell):
    def get_cooldown(self):
        return 20

    def perform(self):
        Global.world.location.sound.register(self.host.pos, 3, file='spell')
        for x in range(-2, 3):
            for y in range(-2, 3):
                tile = self.host.pos.get_neighbor(x, y)
                if tile and not tile.things:
                    Stock.make('Fog', tile)


class Find(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 200

    def perform(self):
        Global.world.location.sound.register(self.host.pos, 3, file='spell')
        from src.tools.Data import Data
        armor = Global.r.rand_list(Data.get_line('raw.txt', 'find')[1])
        Stock.make(armor, self.host.pos)


class Phantom(Spell):
    def get_range(self):
        return 9

    def perform(self):
        target = self.auto_target(0)
        if target:
            Global.world.location.sound.register(target.pos, 8, file='void')
            Particle.make('mist', target.pos)
            if isinstance(target, Item):
                if not target.host:
                    phantom = Stock.make('Phantom', target.pos)
                    phantom.set_host(target)
                    phantom.states.add('Script', 240, 'remove')
                    from src.game.ScriptManual import ScriptManual
                    ScriptManual.ally(self.host, phantom)
                    return


class Pester(Spell):
    def get_cooldown(self):
        return 20

    def perform(self):
        target = self.auto_target(2)
        if target:
            Global.world.location.sound.register(target.pos, 8, file='void')
            for i in range(Global.r.rand_int(2, 4)):
                space = target.pos.get_neighbor(Global.r.rand_int(-3, 3), Global.r.rand_int(-3, 3), limit=True)
                summon = Stock.make('Moth', space)
                Particle.make('zwip', space)
                summon.tags.set('team', self.host.tags.get('team', 0))
                Global.world.location.population.adjust(summon)
                pos = target.pos - space
                summon.tags.set('tgt', 'x' + str(pos.x) + 'y' + str(pos.y))
                summon.tags.set('task', 'Attack')
                summon.pilot.load('wander')
                summon.states.add('Script', 24, 'remove')


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
            Global.world.location.sound.register(self.host.pos, 8, file='void')


class Transmogrify(Spell):
    def get_cooldown(self):
        return 40

    def perform(self):
        target = self.auto_target(2)
        if target:
            Global.world.location.sound.register(target.pos, 8, file='void')
            from src.entity.unit.Unit import Unit
            if isinstance(target, Unit):
                from src.tools.Data import Data
                pick = Data.get_line('raw.txt', 'transmogrify')[1]
                duration = 150
                target.states.add('Shapeshift', duration, Global.r.rand_list(pick))


class Snare(Spell):
    def get_cooldown(self):
        return 20

    def perform(self):
        target = self.auto_target(2)
        if target:
            Global.world.location.sound.register(target.pos, 1, file='drain')
            Particle.make('zap', target.pos)
            target.states.add('Speed', 60, -20)


class Fireball(Spell):
    def get_cooldown(self):
        return 20

    def get_range(self):
        return 7

    @staticmethod
    def fn(prev, tile):
        if tile:
            if not tile.is_seen():
                return prev
            if tile.get_solidity() >= Tile.COLLIDE_FOG:
                return tile

    def perform(self):
        if self.host:
            origin = self.host.pos
        else:
            origin = self.host.pos
        r = Stock.make('Fireball', origin)
        r.tags.increment('fuel', 9)
        destination = self.host.pos.get_cardinal(self.host.direction, distance=self.get_range())
        target = Global.world.location.collide_line(self.host.pos.x, self.host.pos.y,
                                                    destination.x, destination.y, self.fn, 10)
        Global.world.location.sound.register(target, 9, file='fire')
        r.relocate(to=target)
        r.states.add('Script', 2, '>buff>*host>Burn>8>0')


class Sting(Spell):
    def get_cooldown(self):
        return 16

    def get_delay(self):
        return 4

    def get_range(self):
        return 12

    def get_motion(self):
        return 'arch'

    def perform(self):
        def fn(prev, tile):
            if tile:
                if not tile.is_seen():
                    return prev
                if tile.get_solidity() >= Tile.COLLIDE_FOG:
                    return tile
        target = self.auto_target(2)
        if target:
            target = Global.world.location.collide_line(self.host.pos.x, self.host.pos.y,
                                                        target.pos.x, target.pos.y, fn, 10)
            r = Stock.make('Arrow', self.host.pos)
            r.face(target.get_face(r.pos))
            r.relocate(to=target)
            Global.world.location.field.register(2, target, delay=1, hitter=self.host)


class Blink(Spell):
    def get_cooldown(self):
        return 4

    def perform(self):
        power = 9
        x = Global.r.rand_int(-power, power)
        y = Global.r.rand_int(-power, power)
        destination = self.host.pos.get_neighbor(x, y, limit=True)
        for i in self.host.pos.things:
            i.move_line(destination)


class Corona(Spell):
    def get_cooldown(self):
        return 4

    def perform(self):
        radius = 13
        duration = 180
        for tile in self.host.pos.get_area(radius, radius):
            for thing in tile.things:
                Particle.make('shock', tile)
                thing.states.add('Glow', duration, 1)
                break


class Push(Spell):
    def get_delay(self):
        return 0

    def get_cooldown(self):
        return 16

    def get_motion(self):
        return 'fly'

    def perform(self):
        target = self.cardinal_target(block=Tile.COLLIDE_ITEM)
        Particle.make('wind', target)
        tile = target.get_cardinal(self.host.direction)
        for i in target.things.copy():
            i.relocate(to=tile)


class Jump(Spell):
    def get_cooldown(self):
        return 20

    def get_motion(self):
        return 'fly'

    def get_delay(self):
        return 0

    def perform(self):
        front = self.host.pos.get_cardinal(self.host.direction, distance=Global.r.rand_int(3, 9))
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
            Global.world.location.sound.register(self.host.pos, 4, file='void')
            Particle.make('zwip', self.host.pos)
            self.host.remove()


class Torment(Spell):
    def get_cooldown(self):
        return 40

    def get_delay(self):
        return 8

    def perform(self):
        targets = self.host.get_team(ally=False)
        for i in targets:
            if (i.pos - self.host.pos).difference() <= 9:
                Global.world.location.sound.register(i.pos, 9, file='fire')
                i.states.add('Burn', 12)


class Avatar(Spell):
    def perform(self):
        golem = Stock.make('Golem', self.host.pos)
        x = Global.r.rand_int(-1, 1)
        y = Global.r.rand_int(-1, 1)
        destination = self.host.pos.get_neighbor(x, y, limit=True)
        golem.move_line(destination)
        from src.game.ScriptManual import ScriptManual
        ScriptManual.ally(self.host, golem)
        golem.states.add('Script', 240, 'remove')


class Summon(Spell):
    def get_delay(self):
        return 2

    def get_cooldown(self):
        return 16

    def get_range(self):
        return 12

    def perform(self):
        target = self.auto_target(2)
        if target:
            x = Global.r.rand_int(-1, 1)
            y = Global.r.rand_int(-1, 1)
            destination = self.host.pos.get_neighbor(x, y, limit=True)
            Particle.make('wind', target.pos)
            target.move_line(destination)
            target.states.add('Speed', 4, -10)
            Global.world.location.sound.register(target.pos, 4, file='down')


class Barrier(Spell):
    def get_cooldown(self):
        return 80

    def get_delay(self):
        return 2

    def perform(self):
        self.host.states.add('Barrier', 80)
        self.host.states.add('Deflection', 80)


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
            if Global.r.rand_bool():
                Global.world.location.sound.register(self.host.pos, 2, file='void')
                Particle.make('barrier3', target.pos)
                from src.tools.Data import Data
                unit = Stock.get(target.name, data=Data.parse(target.__str__()))
                unit.add()
                x = Global.r.rand_int(-1, 1)
                y = Global.r.rand_int(-1, 1)
                destination = unit.pos.get_neighbor(x, y, limit=True)
                unit.move_line(destination)
            else:
                Global.world.location.sound.register(self.host.pos, 2, file='down')


class Earthquake(Spell):
    def get_delay(self):
        return 8

    def get_cooldown(self):
        return 50

    def perform(self):
        Global.world.location.sound.register(self.host.pos, 0, file='energy')
        targets = self.host.pos.get_area(9, 9)
        for i in targets:
            for thing in i.things.copy():
                Particle.make('spin', i)
                thing.states.add('Knockout', 40)


class Charge(Spell):
    def get_delay(self):
        return 0

    def get_cooldown(self):
        return 20

    def get_motion(self):
        return 'bash'

    def perform(self):
        front = self.host.pos.get_cardinal(self.host.direction, distance=3)
        self.host.move_line(front, flag=self.host.collision_type)
        front = self.host.pos.get_cardinal(self.host.direction)
        Global.world.location.field.register(1, front, delay=0, hitter=self.host)
        self.host.action.make('bash', 8)


class Sanctuary(Spell):
    def get_delay(self):
        return 14

    def get_cooldown(self):
        return 100

    def perform(self):
        center_x = self.host.pos.x
        center_y = self.host.pos.y
        radius = 3
        from src.entity.unit.Unit import Unit
        for x in range(center_x - radius, center_x + radius + 1):
            for y in range(center_y - radius, center_y + radius + 1):
                tile = Global.world.location.get_tile(x, y)
                if tile:
                    for thing in tile.things.copy():
                        if thing != self.host and (not isinstance(thing, Item) or thing.host != self.host):
                            if isinstance(thing, Unit):
                                direction = self.host.pos.get_face(thing.pos)
                                destination = thing.pos.get_cardinal(direction, distance=radius)
                                thing.move_line(to=destination, flag=thing.collision_type + 1)
                            else:
                                thing.remove()
                    if x == center_x - radius or x == center_x + radius or\
                            y == center_y - radius or y == center_y + radius:
                        Stock.make('Fog', tile)
                    elif tile.get_yield() >= -10:
                        tile.set_terrain('M')


class Breeze(Spell):
    def get_delay(self):
        return 8

    def get_cooldown(self):
        return 100

    def perform(self):
        self.host.states.add('Levitation', 80, 0)
        self.host.states.add('Speed', 80, 4)


class Capture(Spell):
    def get_delay(self):
        return 12

    def get_cooldown(self):
        return 100

    def get_range(self):
        return 1

    def perform(self):
        ego = self.host.states.get('Ego')
        if ego:
            ego.end()
        else:
            target = self.auto_target(0)
            if target and target != Global.player.character:
                Global.world.location.sound.register(self.host.pos, 0, file='drain')
                Particle.make('portal', target.pos)
                self.host.states.add('Ego', -1, target.__str__())
                target.remove()


class Timesave(Spell):
    def get_delay(self):
        return 24

    def get_cooldown(self):
        return 200

    def perform(self):
        targets = self.host.pos.get_area(4, 4)
        for i in targets:
            for thing in i.things:
                thing.states.add('Revive', 160, 0)
