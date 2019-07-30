from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Task import *
from src.entity.unit.item.Item import Item


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


class Pilot(Manual):
    def __init__(self, host):
        super().__init__(host)
        self.priority = 5
        self.range = 6
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
            self.perceive(self.range)
            if self.task.is_done() and self.task.next:
                self.task = self.task.next
                self.task.on_set()
            self.task.perform()

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
            aoe = self.host.location.get_area(self.host.pos[0] + (offset[0], 0), sight + offset[1], sight + offset[1])
            for i in aoe:
                for thing in i.things:
                    if thing != self.host:
                        perceived.append(thing)
            if self.priority > 2:
                targets = []
                items = []
                host_pos = self.host.pos[0].get_center().to_list()
                for thing in perceived:
                    to = (thing.pos[0] - self.host.pos[0]).to_list()
                    sight = self.host.location.collide_sight(host_pos, to)
                    if sight:
                        if isinstance(thing, Unit):
                            if Faction.is_against(self.host.faction, thing.faction):
                                targets.append(thing)
                        elif isinstance(thing, Item) and not thing.host:
                            items.append(thing)
                if targets:
                    self.spot_enemy(targets)
                elif items and self.priority > 3:
                    self.spot_item(items)

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = targets[0]
        for i in targets:
            t = (i.pos[0] - self.host.pos[0]).distance()
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
        aoe = self.host.location.get_area(self.host.pos[0], 4, 2)
        for i in aoe:
            for thing in i.things:
                if thing != self.host and not Faction.is_against(thing.faction, self.host.faction):
                    if isinstance(thing, Unit) and not isinstance(thing.pilot, Manual) and thing.pilot.priority > 2:
                        thing.pilot.spot_enemy(targets)

    def spot_item(self, targets):
        pass

    def get_routes(self, pos):
        options = []
        right = self.host.location.get_tile(pos + (1, 0))
        upright = self.host.location.get_tile(pos + (1, -1))
        left = self.host.location.get_tile(pos + (-1, 0))
        upleft = self.host.location.get_tile(pos + (-1, -1))
        ground = self.host.location.get_tile(pos + (0, 1))
        air = self.host.location.get_tile(pos + (0, -1))
        if ground.is_land(Tile.CHECK_LANDABLE) or pos.is_climbable():
            if not air.is_land(Tile.CHECK_LARGE) and air.is_climbable():
                options.append((0, -1))
            if not right.is_land(Tile.CHECK_LARGE):
                if self.host.location.get_tile(pos + (1, 1)).is_land(Tile.CHECK_LANDABLE) or right.is_climbable():
                    options.append((1, 0))
                else:
                    options.append((1, 1))
            elif not upright.is_land(Tile.CHECK_LARGE):
                options.append((1, -1))
            if not left.is_land(Tile.CHECK_LARGE):
                if self.host.location.get_tile(pos + (-1, 1)).is_land(Tile.CHECK_LANDABLE) or left.is_climbable():
                    options.append((-1, 0))
                else:
                    options.append((-1, 1))
            elif not upleft.is_land(Tile.CHECK_LARGE):
                options.append((-1, -1))
            if not ground.is_land(Tile.CHECK_LARGE) and ground.is_climbable() and ground.y < self.host.location.edge:
                options.append((0, 1))
        else:
            options.append((0, 1))
        return options
