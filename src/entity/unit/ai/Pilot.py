from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Task import *


class Manual:
    def __init__(self, host):
        self.host = host
        self.task = Idle(self)
        self.var = None

    def __str__(self):
        return self.__class__.__name__

    def hit(self):
        pass

    def update(self):
        pass

    def hear(self, pos):
        pass


class Pilot(Manual):
    def __init__(self, host):
        super().__init__(host)
        self.priority = 5
        self.move = None
        self.hunt = None
        self.init()

    def init(self):
        self.move = Move(self, 1)
        self.hunt = Hunt(self)
        self.hunt.move = self.move
        self.hunt.attack = Attack(self)

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            sight = self.get_sight()
            self.perceive(sight, offset=(max(0, sight - 1), 0))
            if self.task.is_done() and self.task.next:
                self.task = self.task.next
                self.task.on_set()
            self.task.perform()

    def get_sight(self):
        return max(self.host.attributes.agility, int(self.host.location.sight_range / 2))

    def add_task(self, task):
        task.next = self.task
        self.task = task
        self.task.on_set()

    def hit(self):
        if self.priority > 1:
            self.priority = 3
            self.add_task(Search(self))

    def perceive(self, sight, offset=(0, 0)):
        if self.priority > 1:
            perceived = []
            aoe = self.host.location.get_area(self.host.pos + (offset[0], 0), sight + offset[1], sight + offset[1])
            for i in aoe:
                for thing in i.things:
                    if thing != self.host:
                        perceived.append(thing)
            if self.priority > 2:
                targets = []
                host_pos = self.host.pos.get_center().to_list()
                for thing in perceived:
                    to = (thing.pos - self.host.pos).to_list()
                    sight = self.host.location.collide_sight(host_pos, to)
                    if sight:
                        if isinstance(thing, Unit):
                            if self.host.faction != thing.faction:
                                targets.append(thing)
                if targets:
                    self.spot_enemy(targets)

    def hear(self, pos):
        if self.priority > 3:
            self.add_task(Search(self, target=pos))

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = targets[0]
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                nearest_dist = t
                nearest = i
        return nearest

    def spot_enemy(self, targets):
        self.priority = 1
        self.var = self.prioritize(targets)
        self.add_task(self.hunt)
        from src.entity.Effect import Effect
        Effect.make('shout', self.host.vec)
        self.host.location.sound.register(self.host.pos, 16)

    def get_routes(self, pos):
        options = []
        right = self.host.location.get_tile(pos + (1, 0))
        upright = self.host.location.get_tile(pos + (1, -1))
        left = self.host.location.get_tile(pos + (-1, 0))
        upleft = self.host.location.get_tile(pos + (-1, -1))
        ground = self.host.location.get_tile(pos + (0, 1))
        air = self.host.location.get_tile(pos + (0, -1))
        if not air.is_land(Tile.CHECK_FIRM) and (air.is_climbable() or pos.is_climbable()):
            options.append((0, -1))
        if not right.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (1, 1)).is_land(self.host.standables):
                options.append((1, 0))
            else:
                options.append((1, 1))
        elif not upright.is_land(Tile.CHECK_FIRM):
            options.append((1, -1))
        if not left.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (-1, 1)).is_land(self.host.standables):
                options.append((-1, 0))
            else:
                options.append((-1, 1))
        elif not upleft.is_land(Tile.CHECK_FIRM):
            options.append((-1, -1))
        if not ground.is_land(Tile.CHECK_FIRM) and ground.is_climbable():
            options.append((0, 1))
        return options
