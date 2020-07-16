from src.entity.Particle import Particle
from src.game import Global
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Buff:
    def __init__(self, host, name, duration, var):
        self.name = name
        self.host = host
        self.duration = duration
        self.var = var
        self.frame = 0

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',' + str(self.var) + ']'

    def get_tags(self):
        return []

    def get_display_name(self):
        return self.name.title()

    def describe_duration(self):
        if self.duration == -1:
            return Dialog.get('persistent')
        else:
            return str(self.duration)

    def describe(self):
        r = self.get_display_name()
        r += '\n' + Dialog.get('Duration') + ': ' + self.describe_duration()
        from src.tools.Data import Data
        data = Data.get_line('descriptions.txt', self.name)
        if data:
            r += '\n' + data[1]
        return r

    def update(self):
        if self.duration == 0:
            return 1
        elif self.duration > 0:
            self.duration -= 1

    def effect(self, frame):
        self.frame += 1
        return not self.frame % frame

    def end(self):
        self.duration = 0

    def is_valid(self):
        return not self.host.states.get('Immune')

    def on_start(self):
        pass

    def on_load(self):
        pass

    def on_stack(self, duration, var):
        pass

    def on_finish(self):
        pass

    def on_update(self):
        pass

    def trigger(self, arg):
        pass


class StatBuff(Buff):
    def get_stat(self):
        return 'p', 'Durability'

    def get_tags(self):
        if self.var < 0:
            return ['magic', 'harm']
        return ['magic']

    def get_display_name(self):
        return 'Status' + ' (' + Dialog.sign(self.var) + ' ' + self.get_stat()[1] + ')'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        Particle.make('wind', self.host.pos)
        self.host.tags.increment(self.get_stat()[0], self.var)

    def on_finish(self):
        self.host.tags.increment(self.get_stat()[0], -self.var)

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'act' and arg[1] in ['hit']:
            self.end()


class Glow(Buff):
    def get_tags(self):
        return ['magic', 'stack']

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = max(self.var, var)

    def on_update(self):
        self.host.pos.glow(self.var)

    def on_finish(self):
        self.host.pos.glow_stop()


class Revive(Buff):
    def stuff(self):
        pass


class Health(Buff):
    def get_tags(self):
        if self.var < 0:
            return ['magic', 'harm']
        return ['magic']

    def get_display_name(self):
        if self.var < 0:
            return 'Harm'
        return self.name

    def apply(self):
        self.host.decay(-self.var)

    def on_start(self):
        self.apply()

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var
        self.apply()

    def on_update(self):
        if self.effect(10):
            self.apply()


class Brand(Buff):
    def get_tags(self):
        return ['stack']

    def get_display_name(self):
        return self.var

    def trigger(self, arg):
        if arg[0] == 'attack':
            from src.game.Script import Script
            Script.var['host'] = arg[1]
            Script.execute_code(self.var)


class Burn(Buff):
    def get_tags(self):
        return ['magic', 'harm', 'stack']

    def is_valid(self):
        if self.host.tags.get('fuel', 1) > 0:
            return super().is_valid()

    def on_start(self):
        self.duration += self.host.tags.get('fuel', 1) * 10
        if self.duration >= 90:
            self.host.location.sound.register(self.host.pos, 13, file='critical')
            for y in range(-1, 2):
                for x in range(-1, 2):
                    tile = self.host.pos.get_neighbor(x, y)
                    if tile:
                        Particle.make('explode', tile, glow=1)
                        for i in tile.things:
                            i.hit(int(self.duration / 10), hitter=None)

    def on_update(self):
        self.var += 1
        if not self.var % 2:
            self.host.pos.glow(4)
            Particle.make('burn', self.host.pos, glow=1)
            if not self.var % 8:
                self.var = 0
                self.host.decay(1)
                from src.entity.Stock import Stock
                if self.host.pos.get_name().startswith('wood') and Global.r.rand_int(1, 8) == 1:
                    Stock.make('Plank', self.host.pos)
                    self.host.pos.set_terrain('.')
                else:
                    x = Global.r.rand_int(-1, 1)
                    y = Global.r.rand_int(-1, 1)
                    neighbor = self.host.pos.get_neighbor(x, y)
                    if neighbor:
                        if not neighbor.things and neighbor.get_name().startswith('wood'):
                            Stock.make('Flame', neighbor)
                        else:
                            for thing in neighbor.things:
                                thing.states.add('Burn', 12)


class Effect(Buff):
    def get_tags(self):
        return ['magic', 'hide']

    def on_update(self):
        if self.effect(6):
            Particle.make(self.var, self.host.pos)


class Speed(StatBuff):
    def get_stat(self):
        return 'spd', 'Speed'


class Fatigue(StatBuff):
    def get_stat(self):
        return 'aspd', 'Fatigue'


class Damage(StatBuff):
    def get_stat(self):
        return 'DMG', 'Strength'


class Invisible(Buff):
    def __init__(self, host, name, duration, var):
        super().__init__(host, name, duration, var)
        self.orig = None

    def get_tags(self):
        return ['magic', 'stack']

    def is_valid(self):
        if not self.host.states.get('Invisible'):
            return super().is_valid()

    def on_start(self):
        Particle.make('mist', self.host.pos)
        self.on_load()
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            for unit in self.host.get_team(ally=False):
                if unit.pilot.priority == 1:
                    unit.pilot.lose(self.host)

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var

    def on_load(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.tags.increment('sth', 40)

    def on_finish(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.tags.increment('sth', -40)
        self.host.show(True)

    def on_update(self):
        if Global.player.player_mode == 1:
            self.host.show(False)

    def trigger(self, arg):
        super().trigger(arg)
        self.host.show(True)  # Show before dropping item
        self.end()


class Invulnerability(Buff):
    def is_valid(self):
        if not self.host.hittable:
            return super().is_valid()

    def on_start(self):
        self.host.hittable = 0

    def on_finish(self):
        self.host.hittable = 1


class Immune(Buff):
    def stuff(self):
        pass


class Script(Buff):
    def on_finish(self):
        from src.game.Script import Script
        Script.var['host'] = self.host
        Script.execute_code(self.var)


class Spell(Buff):
    def on_finish(self):
        from src.entity.unit.item.Spell import Spell
        Spell.get(self.var, power=self.duration).cast(self.host, delay=0)


class Shapeshift(Buff):
    def get_tags(self):
        return ['stack']

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\'' + self.var + '\']'

    def on_start(self):
        var = self.var
        self.host.states.buffs.remove(self)
        self.var = self.host.__str__()
        self.host.states.buffs.append(self)
        from src.game.ScriptManual import ScriptManual
        ScriptManual.shapeshift(self.host, var)

    def on_finish(self):
        data = Data.parse(self.var)
        from src.game.ScriptManual import ScriptManual
        old_host = self.host
        ScriptManual.shapeshift(self.host, data[1], data=data).relocate(to=old_host.pos, force=True)


class Concentration(Buff):
    def get_tags(self):
        return ['hide', 'stack']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def effect_on_load(self):
        if self.host.get_skill('heightened sense'):
            copy = self.host.sight
            from src.map.Tile import Tile
            new = []
            for i in copy:
                if i != Tile.COLLIDE_FOG:
                    new.append(i)
            self.host.sight = new

    def on_start(self):
        Particle.make('sweat', self.host.pos, offset=4)
        self.effect_on_load()
        if self.host.get_skill('iron will'):
            for i in self.host.states.buffs:
                if 'harm' in i.get_tags():
                    Particle.make('barrier', self.host.pos, offset=4)
                    i.end()
                    self.end()
                    return
        if self.host.get_skill('hide'):
            self.host.states.add('Invisible', -1)
        if self.host.get_skill('weave'):
            for i in self.host.pos.things:
                if i.name == 'Web':
                    return
            from src.entity.Stock import Stock
            Stock.make('Web', self.host.pos)

    def on_load(self):
        self.effect_on_load()

    def on_finish(self):
        if self.host.get_skill('heightened sense'):
            from src.map.Tile import Tile
            self.host.sight.append(Tile.COLLIDE_FOG)

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'spend':
            if not self.host.get_skill('concentration') or Global.r.rand_int(0, 3) != 0:
                self.host.action.idle_frame = 0
                Particle.make('sweat', self.host.pos)
                self.duration = 1


class Vengeance(Buff):
    def get_tags(self):
        return ['stack']

    def on_stack(self, duration, var):
        self.var += 1
        self.duration = duration
        if self.var >= 3:
            from src.entity.unit.Actions import Actions
            for i in Global.cardinal_coord:
                tile = self.host.pos.get_neighbor(i[0], i[1])
                if tile:
                    for thing in tile.things:
                        thing.move_line(tile)
                        Actions.knockdown(thing)
                    Particle.make('batter', tile)
            self.host.location.sound.register(self.host.pos, 1, file='critical')
            self.end()


class Lignification(Buff):
    def get_tags(self):
        return ['magic']

    def is_valid(self):
        mat = self.host.tags.get('mat')
        if mat and mat != 'wood':
            return super().is_valid()

    def on_start(self):
        Particle.make('mist', self.host.pos)
        self.host.tags.increment('fuel', 2)
        self.host.tags.increment('def', 2)
        self.host.tags.increment('spd', -1)

    def on_finish(self):
        self.host.tags.increment('fuel', 2, remove=1)
        self.host.tags.increment('def', -2, remove=0)
        self.host.tags.increment('spd', 1, remove=0)


class Petrification(Buff):
    def get_tags(self):
        return ['magic']

    def describe(self):
        return 'Incoming damage reduced by 5 but become immobile and slow attack speed.'

    def is_valid(self):
        mat = self.host.tags.get('mat')
        if mat and mat != 'metal':
            return super().is_valid()

    def on_start(self):
        Particle.make('mist', self.host.pos)
        self.host.tags.increment('fuel', -1)
        self.host.tags.increment('aspd', -5)
        self.host.tags.increment('def', 5)
        self.host.tags.increment('spd', -12)

    def on_finish(self):
        self.host.tags.increment('fuel', 1, remove=1)
        self.host.tags.increment('aspd', 5, remove=0)
        self.host.tags.increment('def', -5, remove=0)
        self.host.tags.increment('spd', 12, remove=0)


class Vision(Buff):
    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\'' + self.var + '\']'

    def get_tags(self):
        return ['magic']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        Particle.make('portal', self.host.pos)
        self.var = Dialog.nonstrlist(self.host.sight)
        from src.map.Tile import Tile
        self.host.sight = [Tile.COLLIDE_MAGIC]

    def on_load(self):
        from src.map.Tile import Tile
        self.host.sight = [Tile.COLLIDE_MAGIC]

    def on_finish(self):
        self.host.sight = Data.parse(self.var)[0]

    def trigger(self, arg):
        super().trigger(arg)
        self.end()


class Levitation(Buff):
    def get_tags(self):
        return ['magic']

    def is_valid(self):
        return not self.host.tags.get('fly')

    def on_start(self):
        Particle.make('zip', self.host.pos)
        self.host.tags.set('fly', 1)
        self.on_load()

    def on_load(self):
        self.var = str(self.host.collision_type)
        from src.map.Tile import Tile
        self.host.collision_type = Tile.COLLIDE_TERRAIN

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var

    def on_finish(self):
        self.host.collision_type = int(self.var)
        self.host.tags.remove('fly')

    def trigger(self, arg):
        if arg[0] == 'act' and arg[1] == 'hit':
            self.end()
            from src.entity.unit.Actions import Actions
            Actions.knockdown(self.host)

    def on_update(self):
        if self.effect(6):
            Particle.make('zip', self.host.pos)


class Poison(Buff):
    def get_tags(self):
        return ['magic', 'harm', 'stack']

    def get_display_name(self):
        return super().get_display_name() + ' (' + str(self.var) + ')'

    def on_update(self):
        if self.effect(12):
            Particle.make('poison', self.host.pos)

    def update(self):
        if self.duration == 0:
            return 1

    def trigger(self, arg):
        if arg[0] == 'time':
            self.host.decay(arg[1] * self.var)
            self.duration = max(0, self.duration - arg[1])


class Knockout(Buff):
    def get_tags(self):
        return ['harm', 'stack']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        self.host.action.set('fall')
        self.host.action.delay = self.duration

    def on_load(self):
        self.on_start()

    def trigger(self, arg):
        if arg[0] == 'act' and arg[1] == 'hit':
            self.end()
            if self.host.action.current_action == 'fall':
                self.host.action.delay = 1
