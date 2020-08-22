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

    def describe(self):
        r = self.get_display_name()
        r += '\n' + Dialog.get('Duration') + ': ' + Dialog.duration(self.duration)
        from src.tools.Data import Data
        data = Data.get_line('descriptions.txt', self.name.lower())
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
        if 'magic' in self.get_tags() and 'harm' in self.get_tags():
            deflect = self.host.states.get('Deflection')
            if deflect:
                deflect.trigger()
                return False
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
        return Dialog.sign(self.var) + ' ' + Dialog.get(self.get_stat()[1])

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
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
    def get_tags(self):
        return ['stack']

    def on_start(self):
        cell_coord = [str(x) for x in Global.world.get_tile_true_pos(self.host.pos.x, self.host.pos.y)]
        self.var = '&'.join(cell_coord)
        self.host.tags.set('corpse', 0)
        Particle.make('barrier3', self.host.pos, glow=4)

    def on_stack(self, duration, var):
        self.duration = max(self.duration, duration)
        self.var = var

    def on_finish(self):
        self.host.tags.remove('corpse')


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

    def trigger(self, arg):
        if arg[0] == 'attack':
            from src.game.Script import Script
            if arg[1].removed == 0:
                Script.var['host'] = arg[1]
                Script.execute_code(self.var)


class Burn(Buff):
    def get_tags(self):
        return ['magic', 'harm', 'stack']

    def is_valid(self):
        if self.host.tags.get('fuel', 1) > 0:
            return super().is_valid()

    def on_start(self):
        self.duration += min(120, self.host.tags.get('fuel', 1) * 10)
        if self.duration >= 90:
            self.host.location.sound.register(self.host.pos, 13, file='critical')
            for y in range(-1, 2):
                for x in range(-1, 2):
                    tile = self.host.pos.get_neighbor(x, y)
                    if tile:
                        Particle.make('explode', tile, glow=1, offset=4)
                        for i in tile.things:
                            if i.hit(1, hitter=None) != 2:
                                i.decay(1)
        else:
            self.host.decay(1)

    def on_update(self):
        self.var += 1
        if not self.var % 4:
            self.host.pos.glow(8)
            Particle.make('burn', self.host.pos, glow=1, offset=12)
            if not self.var % 8:
                self.var = 0
                from src.entity.Stock import Stock
                if self.host.pos.has_tag('wood') and Global.r.rand_int(1, 8) == 1:
                    Stock.make('Plank', self.host.pos)
                    self.host.pos.set_terrain('.')
                    Global.world.dirty_pos(self.host.pos.x, self.host.pos.y)
                else:
                    x = Global.r.rand_int(-1, 1)
                    y = Global.r.rand_int(-1, 1)
                    neighbor = self.host.pos.get_neighbor(x, y)
                    if neighbor:
                        if not neighbor.things and neighbor.has_tag('wood'):
                            Stock.make('Flame', neighbor)
                        else:
                            for thing in neighbor.things:
                                thing.states.add('Burn', 12)


class Effect(Buff):
    def get_tags(self):
        return ['magic', 'hide']

    def on_update(self):
        if self.effect(6):
            Particle.make(self.var, self.host.pos, offset=12)


class Speed(StatBuff):
    def get_stat(self):
        return 'spd', 'Speed'

    def on_start(self):
        from src.entity.unit.item.Item import Item
        if self.var > 0 and isinstance(self.host, Item):
            if self.host.enhance(Global.r.rand_int(1, min(100, self.duration))):
                self.host.tags.set('skill', 'deft')
        super().on_start()


class Damage(StatBuff):
    def get_stat(self):
        return 'dmg', 'Strength'

    def on_start(self):
        from src.entity.unit.item.Item import Item
        if isinstance(self.host, Item):
            if self.host.enhance(Global.r.rand_int(1, min(100, self.duration))):
                if self.var > 0:
                    self.host.tags.increment('dmg', 1)
                elif self.var < 0:
                    self.host.tags.increment('dmg', -1)
        super().on_start()


class Armoring(StatBuff):
    def get_stat(self):
        return 'def', 'Defense'

    def on_start(self):
        from src.entity.unit.item.Item import Item
        if isinstance(self.host, Item):
            if self.host.enhance(Global.r.rand_int(1, min(100, self.duration))):
                if self.var > 0:
                    self.host.tags.increment('def', 1)
                elif self.var < 0:
                    self.host.tags.increment('def', -1)
        super().on_start()


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
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.tags.increment('sth', 40)
            for unit in self.host.location.population.get_units():
                if unit.pilot.priority == 1:
                    unit.pilot.lose(self.host)

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var

    def on_finish(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            self.host.tags.increment('sth', -40)
        self.host.show(True)

    def on_update(self):
        self.host.show(False)

    def trigger(self, arg):
        super().trigger(arg)
        self.host.show(True)  # Show before dropping item
        self.end()


class Invincible(Buff):
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
    def on_start(self):
        from src.entity.unit.item.Spell import Spell
        Spell.get(self.var).cast_on(self.host)
        self.end()


class Shapeshift(Buff):
    def get_tags(self):
        return ['stack', 'harm']

    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\\' + self.var + '\\]'

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

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
        old_pos = self.host.pos
        ScriptManual.shapeshift(self.host, data[1], data=data).relocate(to=old_pos, force=True)


class Concentration(Buff):
    def get_tags(self):
        return ['hide', 'stack']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def effect_on_load(self):
        if self.host.get_skill('deep sense') and not self.host.states.get('Vision'):
            self.host.states.add('Vision', 8)
        if self.host.get_skill('iron will'):
            self.host.states.add('Deflection', -1)
        if self.host.get_skill('hide'):
            self.host.states.add('Invisible', -1)

    def on_stack(self, duration, var):
        self.effect_on_load()

    def on_start(self):
        Particle.make('sweat', self.host.pos, offset=4)
        self.effect_on_load()
        if self.host.get_skill('weave'):
            for i in self.host.pos.things:
                if i.name == 'Web':
                    return
            from src.entity.Stock import Stock
            Stock.make('Web', self.host.pos)

    def on_load(self):
        self.effect_on_load()

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'spend':
            self.host.action.idle_frame = 0
            self.end()


class Lignification(Buff):
    def get_tags(self):
        return ['magic']

    def on_start(self):
        Particle.make('mist', self.host.pos)
        from src.entity.unit.item.Item import Item
        if isinstance(self.host, Item):
            if self.host.enhance(Global.r.rand_int(1, min(100, self.duration))):
                rand_int = Global.r.rand_int(1, 4)
                self.host.tags.increment('P', rand_int)
                self.host.tags.increment('p', rand_int)
        self.host.tags.increment('fuel', 2)
        self.host.tags.increment('def', 2)
        self.host.tags.increment('spd', -12)

    def on_finish(self):
        self.host.tags.increment('fuel', -2, remove=1)
        self.host.tags.increment('def', -2, remove=0)
        self.host.tags.increment('spd', 12, remove=0)


class Vision(Buff):
    def __str__(self):
        return '[' + self.name + ',' + str(self.duration) + ',\\' + self.var + '\\]'

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
        self.host.sight = [Tile.COLLIDE_TERRAIN]

    def on_load(self):
        from src.map.Tile import Tile
        self.host.sight = [Tile.COLLIDE_TERRAIN]

    def on_finish(self):
        self.host.sight = Data.parse(self.var)[0]

    def trigger(self, arg):
        super().trigger(arg)
        if arg[0] == 'act' and arg[1] == 'hit':
            self.end()


class Levitation(Buff):
    def get_tags(self):
        return ['magic']

    def is_valid(self):
        return not self.host.tags.get('fly')

    def on_start(self):
        Particle.make('zip', self.host.pos, offset=8)
        from src.entity.unit.item.Item import Item
        if isinstance(self.host, Item):
            w = self.host.tags.get('w', 1)
            if w > 1:
                if self.host.enhance(Global.r.rand_int(1, min(100, self.duration))):
                    self.host.tags.increment('w', -1)
            self.end()
        else:
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
        if arg[0] == 'act' and arg[1] == 'hit' and arg[2] > 0:
            self.end()
            from src.entity.unit.Actions import Actions
            Actions.knockdown(self.host, 8)

    def on_update(self):
        if self.effect(6):
            Particle.make('zip', self.host.pos, offset=8)


class Poison(Buff):
    def get_tags(self):
        return ['magic', 'harm', 'stack']

    def get_display_name(self):
        return super().get_display_name() + ' (' + str(self.var) + ')'

    def on_update(self):
        if self.effect(12):
            Particle.make('poison', self.host.pos, offset=8)

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
        if arg[0] == 'act' and arg[1] == 'hit' and arg[2] > 0:
            self.end()
            if self.host.action.current_action == 'fall':
                self.host.action.delay = 1


class Amnesia(Buff):
    def get_tags(self):
        return ['harm']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_start(self):
        self.host.skills.pop()


class Safeguard(Buff):
    def get_tags(self):
        return ['magic', 'stack']

    def on_stack(self, duration, var):
        self.duration = duration
        self.var = var

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_update(self):
        if self.effect(12):
            Particle.make('barrier', self.host.pos)

    def trigger(self, arg):
        if arg[0] == 'act' and arg[1] in ['hit'] and arg[2] > 0:
            from src.entity.unit.item.Spell import Spell
            Spell.get('Evacuate').cast_on(self.host)
            self.end()


class Exhaustion(Buff):
    def get_tags(self):
        return ['harm']

    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()


class Barrier(Buff):
    def get_tags(self):
        return ['magic']

    def trigger(self, arg):
        if arg[0] == 'act' and arg[1] == 'hit' and arg[2] > 0:
            self.host.location.sound.register(self.host.pos, 2, file='energy')
            Particle.make('barrier', self.host.pos)
            self.end()


class Deflection(Buff):
    def get_tags(self):
        return ['magic', 'stack']

    def on_stack(self, duration, var):
        self.duration = duration

    def trigger(self, arg):
        if arg[0] == 'spend':
            self.host.location.sound.register(self.host.pos, 2, file='energy')
            Particle.make('barrier2', self.host.pos)
            self.end()
        elif arg[0] == 'act' and arg[1] == 'hit' and arg[2] > 0:
            self.host.location.sound.register(self.host.pos, 2, file='void')
            self.end()


class Nutrition(Buff):
    def is_valid(self):
        from src.entity.unit.Unit import Unit
        if isinstance(self.host, Unit):
            return super().is_valid()

    def on_stack(self, duration, var):
        pass

    def on_start(self):
        self.host.tags.increment('hunger', -self.var)
