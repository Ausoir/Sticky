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

    def update(self):
        pass


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


class Path(Task):  # path finding A*
    class Node:
        def __init__(self, parent, node):
            self.parent = parent
            self.node = node
            self.g = 0
            self.h = 0
            self.f = self.g + self.h

        def set_h(self, destination):
            self.h = (self.node - destination).distance()

        def __str__(self):
            return self.node.__str__()+'/'+str(self.f)

    def __init__(self, pilot):
        super().__init__(pilot)
        self.open = [Path.Node(None, self.host.pos[0])]
        self.closed = []
        self.result = []
        self.counter = 0
        self.heuristic_threshold = 0

    def is_done(self):
        r = super().is_done()
        if r:
            self.reset()
        return r

    def get_pos(self, x, y):
        return self.pilot.var.location.get_tile(x, y)

    def iterate(self, node):
        index = 0
        for k, v in enumerate(self.open):
            if v.f < node.f:
                index = k
                node = v
        self.open.pop(index)
        self.closed.append(node)
        achieved = (node.node - self.pilot.var.pos[0]).difference()
        if achieved < 2:
            return node
        options = []
        right = not self.get_pos(node.node.x + 1, node.node.y).is_land(Tile.CHECK_LARGE)
        left = not self.get_pos(node.node.x - 1, node.node.y).is_land(Tile.CHECK_LARGE)
        if node.node.is_climbable():
            if not self.get_pos(node.node.x, node.node.y - 1).is_land(Tile.CHECK_LARGE):
                options.append((0, -1))
            if right:
                options.append((1, 0))
            if left:
                options.append((-1, 0))
        if self.get_pos(node.node.x, node.node.y + 1).is_land(Tile.CHECK_LARGE):
            if right:
                if self.get_pos(node.node.x + 1, node.node.y + 1).is_land(Tile.CHECK_LARGE):
                    options.append((1, 0))
                else:
                    options.append((1, 1))
            elif not self.get_pos(node.node.x + 1, node.node.y - 1).is_land(Tile.CHECK_LARGE):
                    options.append((1, -1))
            if left:
                if self.get_pos(node.node.x - 1, node.node.y + 1).is_land(Tile.CHECK_LARGE):
                    options.append((-1, 0))
                else:
                    options.append((-1, 1))
            elif not self.get_pos(node.node.x - 1, node.node.y - 1).is_land(Tile.CHECK_LARGE):
                options.append((-1, -1))
        else:
            options.append((0, 1))
        for i in options:
            pos = self.get_pos(node.node.x + i[0], node.node.y + i[1])
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            if conflict:
                if node.g + 1 <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1
                    conflict.set_h(self.pilot.var.pos[0])
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1
            new.set_h(self.pilot.var.pos[0])
            new.f = new.h + new.g
            if new.h < self.heuristic_threshold:
                self.open.append(new)

    def check_loop(self, loop, pos):
        for i in loop:
            if i.node == pos:
                return i

    def perform(self):
        if self.result:
            dist = self.result[0] - self.host.pos[0]
            new_dist = (self.result[len(self.result)-1] - self.pilot.var.pos[0]).difference()
            cur_dist = (self.host.pos[0] - self.pilot.var.pos[0]).difference()
            if cur_dist <= 1:
                pass
            elif cur_dist <= new_dist:
                self.result = []
                self.reset()
            elif dist.difference() == 0:
                self.result.pop(0)
                self.perform()
            elif dist.difference() > 8:
                self.result = []
                self.reset()
            elif dist.y < 0:
                self.host.input('jump', dist)
            else:
                self.host.input('walk', dist)

    def update(self):
        for times in range(3):
            self.counter += 1
            if self.open:
                done = self.iterate(self.open[0])
                if done:
                    result = [done.node]
                    while done.parent:
                        done = done.parent
                        result.insert(0, done.node)
                        if done.node == self.host.pos[0]:
                            break
                    self.result = result
                    self.result.pop(0)
                    self.reset()
                    return
                elif self.counter > 40:
                    self.reset()
            else:
                self.reset()

    def reset(self):
        self.heuristic_threshold = (self.host.pos[0] - self.pilot.var.pos[0]).distance()*2
        self.counter = 0
        self.open = [Path.Node(None, self.host.pos[0])]
        self.closed = []


class Pickup(Task):
    def perform(self):
        super().perform()
        if not self.host.is_armed():
            self.host.input('interact', self.host.next_target)
        return 1


class Attack(Task):
    def perform(self):
        if self.pilot.var and Faction.is_against(self.host.faction, self.pilot.var.faction):
            dist = self.pilot.var.pos[0] - self.host.pos[0]
            reach = self.host.location.collide_line(self.host.get_interact_pos(), dist.x, dist.y,
                                                    distance=1, flag=Tile.CHECK_TERRAIN)
            reach = reach - self.host.get_interact_pos()
            if self.pilot.in_range(abs(dist.x)) and abs(reach.x) >= abs(dist.x):
                if -1 <= dist.y <= 1:
                    self.host.input('use', dist)
                    return 1


class Melee(Task):
    def in_range(self, x):
        for i in self.host.weapon.range:
            if i == x:
                return 1
        return 0

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

    def perform(self):
        if self.pilot.var and Faction.is_against(self.host.faction, self.pilot.var.faction):
            diff = self.pilot.var.pos[0] - self.host.pos[0]
            if self.special(diff):
                return 1
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
                    return 1
