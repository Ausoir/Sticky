from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Behavior import Behavior
from src.entity.unit.ai.Faction import Faction
from src.game.Turn import Turn
from src.map.Tile import Tile
from src.tools.Random import Random


class Pilot:
    def __init__(self, host, fight_type):
        self.host = host
        self.fight_type = fight_type
        if fight_type != 'Manual':
            Turn.add(self)
            self.delay = 0
            self.range = 4
            self.behavior = Behavior(host, fight_type)
            self.behavior.set('idle', None)

    def __str__(self):
        return self.fight_type

    def turn(self):
        if not self.dodge():
            if not self.delay:
                behavior, arguments = self.perceive()
                self.behavior.set(behavior, arguments)
                self.behavior.perform()

    def perceive(self):
        perceived = []
        aoe = self.host.location.get_area(self.host.pos[0], self.range)
        for i in aoe:
            for thing in i.things:
                if thing != self.host:
                    perceived.append(thing)
        if self.behavior.priority >= 2:
            targets = []
            for thing in perceived:
                if isinstance(thing, Unit) and Faction.is_against(self.host.faction, thing.faction):
                    targets.append(thing)
            if targets:
                return 'hunt', targets
        if self.behavior.priority >= 3:
            if perceived:
                return 'react', perceived[Random.rand_int(0, perceived.__len__()-1)]
        return 'idle', None

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
