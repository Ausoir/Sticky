from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Task import *
from src.map.Tile import Tile
from src.tools import Direction


class Manual:
    def __init__(self, host):
        self.host = host
        self.faction = 0  # 0: Neutral, 1: Player, 2: Enemy, 3: Beast, 4: Undead
        self.default = None
        self.move = None
        self.path = None
        self.attack = None
        self.task = None

    def set_task(self, task=None):
        if not task:
            task = self.default
        task.on_set()
        self.task = task

    def hit(self, hitter):
        pass

    def update(self):
        pass

    def hear(self, pos):
        pass


class Pilot(Manual):
    def __init__(self, host):
        super().__init__(host)
        self.priority = 5

    def load(self, arg):
        from src.entity.unit.ai.Routes import Ground
        self.path = Ground(self.host.location)
        if arg == 'neutral':
            self.default = Idle(self)
            self.move = Path(self)
            self.attack = Attack(self)
        elif arg == 'hostile':
            self.default = Idle(self)
            self.move = Path(self)
            self.attack = Attack(self)
        self.task = self.default

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            self.act()

    def act(self):
        if self.priority > 2:
            sight = self.get_sight()
            coord = Direction.coord[self.host.direction]
            targets = self.perceive(sight, offset=[coord[0] * sight, coord[1] * sight])
            if targets:
                self.spot_enemy(targets)
        self.task.perform()

    def get_sight(self):
        return int(Global.map_view.sight_range / 2) + self.priority - 3

    def hit(self, hitter):
        if self.priority > 1:
            self.set_task(self.attack)
            from src.entity.unit.item.Item import Item
            if isinstance(hitter, Unit):
                self.host.tags.set('tgt', hitter.id)
                self.task.target = hitter
            elif isinstance(hitter, Item) and hitter.host:
                self.host.tags.set('tgt', hitter.host.id)
                self.task.target = hitter.host
        else:
            targets = self.perceive(1)
            if targets:
                self.spot_enemy(targets)

    def perceive(self, sight, offset=(0, 0)):
        perceived = []
        aoe = self.host.location.get_area(self.host.pos + (offset[0], offset[1]), sight, int(sight * .8))
        for i in aoe:
            if i.light or abs(i.x - self.host.pos.x) < Global.map_view.view_range:
                for thing in i.things:
                    if thing != self.host and isinstance(thing, Unit):
                        perceived.append(thing)
        targets = []
        for thing in perceived:
            seen = self.host.location.collide_land(self.host.pos, thing.pos, Tile.CHECK_SIGHT)
            if seen == thing.pos:
                if self.host.tags.get('team', 'neutral') != thing.tags.get('team', 'neutral'):
                    targets.append(thing)
        return targets

    def hear(self, pos):
        if self.priority > 3:
            self.move.target = pos
            self.set_task(self.move)

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = None
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                nearest_dist = t
                nearest = i
        return nearest

    def spot_enemy(self, targets):
        var = self.prioritize(targets)
        if var:
            self.host.tags.set('tgt', var.id)
            self.set_task(self.attack)
            self.task.target = var
            from src.entity.Particle import Particle
            Particle.make('shout', self.host.vec)
            self.host.location.sound.register(self.host.pos, 9)
