from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Behavior import Behavior
from src.entity.unit.ai.Task import *
from src.entity.unit.item.Item import Item
from src.map.Tile import Tile
from src.tools.Random import Random


class Pilot:
    def __init__(self, host, fight_type):
        self.host = host
        self.fight_type = fight_type
        self.task = Idle(self)
        self.var = None
        if fight_type == 'Manual':
            def none():
                pass
            self.hit = none
            self.update = none
        else:
            self.priority = 5
            self.delay = 0
            self.range = 4
            self.behavior = Behavior.make(self, fight_type)

    def __str__(self):
        return self.fight_type

    def update(self):
        if self.host.delay == 0:
            if not self.dodge():
                if not self.delay:
                    self.perceive()
                    self.perform()

    def in_range(self, x):
        return x <= 1

    def add_task(self, task):
        task.next = self.task
        self.task = task

    def perform(self):
        self.task.perform()
        if self.task.is_done():
            self.task = self.task.next

    def hit(self):
        self.priority = 3
        self.perceive()

    def perceive(self):
        if self.priority > 1:
            perceived = []
            aoe = self.host.location.get_area(self.host.pos[0], self.range)
            for i in aoe:
                for thing in i.things:
                    if thing != self.host:
                        perceived.append(thing)
            if self.priority > 2:
                targets = []
                items = []
                for thing in perceived:
                    if isinstance(thing, Unit):
                        if Faction.is_against(self.host.faction, thing.faction) and not thing.is_dead():
                            targets.append(thing)
                    elif isinstance(thing, Item):
                        items.append(thing)
                if targets:
                    self.behavior.spot_enemy(self, targets)
                elif items:
                    self.behavior.spot_item(self, items)

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = targets[0]
        for i in targets:
            if not i.is_dead():
                t = (i.pos[0] - self.host.pos[0]).distance()
                if t < nearest_dist:
                    nearest_dist = t
                    nearest = i
        return nearest

    def dodge(self):
        for i in self.host.location.attack.registry:
            if self.host.will_hit(i[1]):
                if self.roll(2):
                    return 1
        return 0

    def roll(self, num):
        for i in range(1, num):
            rand = Random.rand_int(1, 4)
            if rand == 1 and not self.host.location.get_tile(self.host.pos[0] + (1, 0)).is_land(Tile.CHECK_ANY):
                self.host.input('right', (self.host.pos[0] + (1, 0)))
                return 1
            elif rand == 2 and not self.host.location.get_tile(self.host.pos[0] + (-1, 0)).is_land(Tile.CHECK_ANY):
                self.host.input('left', (self.host.pos[0] + (-1, 0)))
                return 1
            elif rand == 3 and not self.host.location.get_tile(self.host.pos[0] + (1, -1)).is_land(Tile.CHECK_ANY):
                self.host.input('jump', self.host.location.get_tile(self.host.pos[0] + (1, -1)))
                return 1
            elif rand == 4 and not self.host.location.get_tile(self.host.pos[0] + (-1, -1)).is_land(Tile.CHECK_ANY):
                self.host.input('jump', self.host.location.get_tile(self.host.pos[0] + (-1, -1)))
                return 1
        return 0
