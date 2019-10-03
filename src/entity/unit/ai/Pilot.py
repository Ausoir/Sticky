from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Task import *
from src.tools.Dialog import Dialog


class Manual:
    def __init__(self, host, var):
        self.host = host
        self.var = {}
        from src.entity.unit.ai import Task as AllTask
        for i in var:
            strings = i.split(':')
            if strings[0] in ['now', 'def', 'move', 'atk']:
                self.var[strings[0]] = getattr(AllTask, strings[1])(self)
            else:
                self.var[strings[0]] = strings[1]
        if 'now' not in self.var:
            if 'def' in self.var:
                self.set_task(self.var['def'])

    def __str__(self):
        return '[' + self.__class__.__name__ + ',' + Dialog.dict(self.var) + ']'

    def set_task(self, task=None):
        if not task:
            task = self.var['def']
        task.on_set()
        self.var['now'] = task

    def hit(self, hitter):
        pass

    def update(self):
        pass

    def hear(self, pos):
        pass

    def get_routes(self, pos):
        options = []
        right = self.host.location.get_tile(pos + (1, 0))
        upright = self.host.location.get_tile(pos + (1, -1))
        left = self.host.location.get_tile(pos + (-1, 0))
        upleft = self.host.location.get_tile(pos + (-1, -1))
        ground = self.host.location.get_tile(pos + (0, 1))
        air = self.host.location.get_tile(pos + (0, -1))
        if not air.is_land(Tile.CHECK_FIRM) and pos.is_climbable():
            options.append((0, -1))
        if not right.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (1, 1)).is_land(self.host.standables):
                options.append((1, 0))
            elif self.host.location.get_tile(pos + (1, 2)).is_land(self.host.standables):
                options.append((1, 1))
        if not upright.is_land(Tile.CHECK_FIRM) and right.is_land(self.host.standables):
            options.append((1, -1))
        if not left.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (-1, 1)).is_land(self.host.standables):
                options.append((-1, 0))
            elif self.host.location.get_tile(pos + (-1, 2)).is_land(self.host.standables):
                options.append((-1, 1))
        if not upleft.is_land(Tile.CHECK_FIRM) and left.is_land(self.host.standables):
            options.append((-1, -1))
        if not ground.is_land(Tile.CHECK_FIRM) and ground.is_climbable():
            options.append((0, 1))
        return options


class Guard(Manual):
    def __init__(self, host, tasks):
        super().__init__(host, tasks)
        self.priority = 5

    def update(self):
        self.var['now'].update()
        if self.host.delay == 0:
            self.act()

    def act(self):
        if self.priority == 5:
            self.perceive(1)
        self.var['now'].perform()

    def perceive(self, sight, offset=(0, 0)):
        aoe = self.host.location.get_area(self.host.pos, sight, sight)
        for i in aoe:
            for thing in i.things:
                if thing != self.host and isinstance(thing, Unit):
                    if self.host.faction != thing.faction and not thing.states.get('Invisible'):
                        self.priority = 1
                        self.var['var'] = thing.id
                        self.var['now'] = self.var['atk']
                        return


class Pilot(Guard):
    def act(self):
        if self.priority > 2:
            sight = self.get_sight()
            targets = self.perceive(sight, offset=(sight * self.host.direction, 0))
            if targets:
                self.spot_enemy(targets)
        self.var['now'].perform()

    def get_sight(self):
        return max(self.host.attributes.intelligence, int(self.host.location.sight_range / 2))

    def hit(self, hitter):
        if self.priority > 1:
            if 'doubt' in self.var and (Global.player.character.pos - self.host.pos).difference() < 16:
                self.set_task(self.var['atk'])
                from src.entity.unit.item.Item import Item
                if isinstance(hitter, Unit):
                    self.var['var'] = hitter.id
                    self.var['now'].target = hitter
                elif isinstance(hitter, Item) and hitter.host:
                    self.var['var'] = hitter.host.id
                    self.var['now'].target = hitter.host
                elif 'ally' not in self.var or Global.player.character.id != self.var['ally']:
                    self.var['var'] = Global.player.character.id
                    self.var['now'].target = Global.player.character
                del self.var['doubt']
            else:
                self.var['doubt'] = 1
                self.set_task(Search(self))
        else:
            targets = self.perceive(1)
            if targets:
                self.spot_enemy(targets)

    def perceive(self, sight, offset=(0, 0)):
        perceived = []
        aoe = self.host.location.get_area(self.host.pos + (offset[0], offset[1]), sight, int(sight/2))
        for i in aoe:
            if i.light or abs(i.x - self.host.pos.x) < self.host.location.view_range:
                for thing in i.things:
                    if thing != self.host:
                        perceived.append(thing)
        targets = []
        host_pos = self.host.pos.get_center().to_list()
        for thing in perceived:
            seen = thing.pos == self.host.pos
            if not seen:
                to = (thing.pos - self.host.pos).to_list()
                seen = self.host.location.collide_sight(host_pos, to)
            if seen:
                if isinstance(thing, Unit):
                    if self.host.faction != thing.faction and not thing.states.get('Invisible'):
                        targets.append(thing)
        return targets

    def hear(self, pos):
        if self.priority > 3:
            self.var['move'].target = pos
            self.set_task(self.var['move'])

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = None
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                if self.reachable(i.pos):
                    nearest_dist = t
                    nearest = i
        return nearest

    def reachable(self, pos):
        routes = self.get_routes(self.host.pos)
        can = pos.x == self.host.pos.x
        can = can or pos.x - self.host.pos.x > 0 and ((1, 0) in routes or (1, 1) in routes or (1, -1) in routes)
        can = can or pos.x - self.host.pos.x < 0 and ((-1, 0) in routes or (-1, 1) in routes or (-1, -1) in routes)
        can = can or pos.y - self.host.pos.y < 0 and (0, -1) in routes
        can = can or pos.y - self.host.pos.y > 0 and (0, 1) in routes
        return can

    def spot_enemy(self, targets):
        var = self.prioritize(targets)
        if var:
            self.var['var'] = var.id
            self.set_task(self.var['atk'])
            self.var['now'].target = var
            from src.entity.Particle import Particle
            Particle.make('shout', self.host.vec)
            self.host.location.sound.register(self.host.pos, 16)


class Sentient(Pilot):
    def __init__(self, host, tasks):
        super().__init__(host, tasks)
        self.move = Path(self)

    def update(self):
        self.var['now'].update()
        if self.host.delay == 0:
            if not self.dodge():
                if self.priority < 3:
                    self.strategize()
                self.act()

    def dodge(self):
        if 'block' in self.host.action.skills:
            for i in self.host.location.attack.registry:
                if i[2] == self.host.pos and i[1] < 3:
                    self.host.input('block', None)
                    return True

    def strategize(self):
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(self.host, Humanoid):
            from src.entity.unit.item.Spell import Spell
            if self.host.weapon.name == 'Bow':
                if self.var['atk'].__class__ != Range:
                    self.var['atk'] = Range(self)
            elif isinstance(self.host.weapon, Spell):
                if self.var['atk'].__class__ != Magic:
                    self.var['atk'] = Magic(self)
            else:
                if self.var['atk'].__class__ != Melee:
                    self.var['atk'] = Melee(self)
