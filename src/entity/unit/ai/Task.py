from src.entity.Space import Space
from src.entity.unit.ai.Faction import Faction
from src.map.Tile import Tile


class Task:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host
        self.next = None
        self.lifetime = 80

    def is_done(self):
        r = self.lifetime == 0
        self.lifetime = 80
        return r

    def perform(self):
        self.lifetime -= 1


class Idle(Task):
    def perform(self):
        self.pilot.priority = 5


class Move(Task):
    def __init__(self, pilot, dist):
        super().__init__(pilot)
        self.distance = dist

    def is_done(self):
        dist = self.pilot.var.pos[0] - self.host.pos[0]
        if abs(dist.x) <= self.distance and abs(dist.y) <= self.distance:
            return 1
        return super().is_done()

    def perform(self):
        super().perform()
        dist = self.pilot.var.pos[0] - self.host.pos[0]
        direction = 1 if dist.x >= 0 else -1
        if dist.y > 1 and dist.x == 0:
            land = self.host.get_offset_tile(0, 1)
            if not land.is_land(Tile.CHECK_TERRAIN):
                self.host.input('use', land - self.host.pos[0])
            return 0
        front = self.host.get_offset_tile(direction, 0)
        top = self.host.get_offset_tile(direction, -1)
        if not front.is_land(Tile.CHECK_LARGE):
            self.host.input('walk', dist)
        elif not top.is_land(Tile.CHECK_LARGE):
            self.host.input('jump', dist)
        elif not top.is_land(Tile.CHECK_TERRAIN):
            self.host.input('use', top - self.host.pos[0])
        elif not front.is_land(Tile.CHECK_TERRAIN):
            self.host.input('use', front - self.host.pos[0])
        return 0


class Travel(Task):  # move & climb
    def __init__(self, pilot, dist):
        super().__init__(pilot)
        self.distance = dist
        self.target = Space(0, 0)
        self.memory = []

    def is_done(self):
        dist = self.pilot.var.pos[0] - self.host.pos[0]
        if abs(dist.x) <= self.distance and abs(dist.y) <= self.distance:
            r = 1
        else:
            r = super().is_done()
        if r:
            self.memory = []
        return r

    def get_horizontal_routes(self, dist):
        direction = 1 if dist.x >= 0 else -1
        front = self.host.get_offset_tile(direction, 0)
        top = self.host.get_offset_tile(direction, -1)
        if not front.is_land(Tile.CHECK_LARGE):
            return 'walk', dist
        elif not top.is_land(Tile.CHECK_LARGE):
            above = self.host.get_offset_tile(0, -1)
            if self.host.pos[0].is_climbable() and above.is_land(Tile.CHECK_BREAKABLE):
                return 'use', above - self.host.pos[0]
            else:
                return 'jump', dist
        elif not top.is_land(Tile.CHECK_TERRAIN):
            return 'use', top - self.host.pos[0]
        elif not front.is_land(Tile.CHECK_TERRAIN):
            return 'use', front - self.host.pos[0]
        return None, None

    def get_vertical_routes(self, dist):
        if dist.x == 0 and dist.y > 1:
            land = self.host.get_offset_tile(0, 1)
            if land.is_climbable():
                return 'duck', dist
            elif not land.is_land(Tile.CHECK_TERRAIN):
                return 'use', land - self.host.pos[0]
        if dist.y < 0:
            above = self.host.get_offset_tile(0, -1)
            if above.is_land(Tile.CHECK_BREAKABLE):
                for i in above.things:
                    if Faction.is_against(self.host.faction, i.faction):
                        self.host.input('use', above - self.host.pos[0])
            elif self.host.hang:
                return 'jump', dist
            blocked = 0
            for i in range(-dist.y):
                if not self.host.get_offset_tile(0, -i).is_climbable():
                    blocked = 1
                    break
            if not blocked:
                if self.host.attributes.leg != 0 and not self.host.hang:
                    return 'idle', dist
                else:
                    return 'jump', dist
        return None, None

    def perform(self):
        super().perform()
        if self.memory:
            for i in self.memory:
                from src.entity.Effect import Effect
                Effect.make('energy', i.get_center())
            self.target = self.memory[self.memory.__len__()-1]
            dist = self.memory[0] - self.host.pos[0]
            if dist.sum() < 3:
                self.memory.pop(0)
                print('pop')
        if self.pilot.var.pos[0] != self.target and abs(self.pilot.var.pos[0].sum() - self.target.sum()) > 2:
            self.memory.append(self.pilot.var.pos[0])
            if self.memory.__len__() > 7:
                self.lifetime = 0
                print('target lost')
        if self.memory:
            self.target = self.memory[0]
        else:
            self.target = self.pilot.var.pos[0]
        dist = self.target - self.host.pos[0]
        if abs(dist.x) > abs(dist.y) and not self.host.hang:
            action, tgt = self.get_horizontal_routes(dist)
            if not action:
                action, tgt = self.get_vertical_routes(dist)
        else:
            action, tgt = self.get_vertical_routes(dist)
            if not action:
                action, tgt = self.get_horizontal_routes(dist)
        if action:
            self.host.input(action, tgt)


class Pickup(Task):
    def perform(self):
        super().perform()
        if not self.host.is_armed():
            self.host.input('interact', self.host.next_target)
        return 1


class Attack(Task):
    def __init__(self, pilot, move):
        super().__init__(pilot)
        self.move = move

    def is_done(self):
        if self.pilot.var.is_dead() or self.move.is_done():
            return 1
        return super().is_done()

    def perform(self):
        super().perform()
        dist = self.pilot.var.pos[0] - self.host.pos[0]
        reach = self.host.location.collide_line(self.host.get_interact_pos(), dist.x, dist.y,
                                                distance=1, flag=Tile.CHECK_TERRAIN)
        reach = reach - self.host.get_interact_pos()
        if self.pilot.in_range(abs(dist.x)) and abs(reach.x) >= abs(dist.x):
            if -1 <= dist.y <= 1:
                self.host.input('use', dist)
                return 0
        if self.move:
            self.move.perform()


class Melee(Task):
    def __init__(self, pilot, move):
        super().__init__(pilot)
        self.move = move

    def in_range(self, x):
        for i in self.host.weapon.range:
            if i == x:
                return 1
        return 0

    def is_done(self):
        if self.pilot.var.is_dead() or self.move.is_done():
            return 1
        return super().is_done()

    def special(self, dist):
        if -1 <= dist.y <= 0:
            if abs(dist.x) == 1 and dist.y == 0 and 'kick' in self.host.action.skills:
                self.host.input('kick', dist)
                return 1
            destination = self.host.location.collide_line(self.host.pos[0], dist.x, 0,
                                                          distance=4, flag=Tile.CHECK_LARGE)
            destination = destination - self.host.pos[0]
            x = min(abs(dist.x), abs(destination.x))
            if x == 1 and 'lunge' in self.host.action.skills:
                self.host.input('lunge', dist)
                return 1
            if 2 <= x <= 3 and 'dash' in self.host.action.skills:
                self.host.input('dash', dist)
                return 1
        return 0

    def perform(self):
        super().perform()
        diff = self.pilot.var.pos[0] - self.host.pos[0]
        if self.special(diff):
            return 0
        longest_range = 0
        for i in self.host.weapon.range:
            if i > longest_range:
                longest_range = i
        reach = self.host.location.collide_line(self.host.get_interact_pos(), diff.x, diff.y,
                                                distance=longest_range, flag=Tile.CHECK_TERRAIN)
        reach = reach - self.host.get_interact_pos()
        dist = int(diff.distance())
        if self.in_range(dist) and int(reach.distance()) >= dist:
            if -1 <= diff.y <= 1:
                self.host.input('use', diff)
                return 0
        if self.move:
            self.move.perform()
