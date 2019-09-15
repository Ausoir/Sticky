from src.entity.Space import Space
from src.game import Global
from src.map.Tile import Tile


class Task:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host
        self.next = None
        self.lifetime = 80

    def is_done(self):
        if not self.lifetime:
            self.lifetime = 80
            return 1

    def perform(self):
        self.lifetime -= 1

    def on_set(self):
        self.pilot.priority = 6

    def update(self):
        pass


class Idle(Task):
    def on_set(self):
        self.pilot.priority = 5

    def perform(self):
        self.pilot.priority = 5
        super().perform()


class Wander(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.direction = 1
        self.direction_y = 0
        self.walk_time = 0
        self.stop = False

    def on_set(self):
        self.pilot.priority = 4
        self.direction = 1 if self.host.attributes.gene % 2 == 0 else -1

    def update(self):
        self.walk_time -= 1
        if self.walk_time < 1:
            self.stop = not self.stop
            self.walk_time = Global.r.rand_int(4, self.host.attributes.gene % 200 + 20)

    def perform(self):
        super().perform()
        if not self.stop:
            routes = self.pilot.get_routes(self.host.pos)
            choice = [0]
            if (0, -1) in routes and self.direction_y != 1:
                choice.append(-1)
            elif (0, 1) in routes and self.direction_y != -1:
                choice.append(1)
            if (self.direction, 0) in routes or (self.direction, 1) in routes:
                choice.append(2)
            elif (self.direction, -1) in routes:
                choice.append(3)
            chosen = Global.r.rand_list(choice)
            if chosen == -1:
                self.direction_y = -1
                self.host.input('jump', Space(0, -1))
            elif chosen == 1:
                self.direction_y = 1
                self.host.input('duck', Space(0, 1))
            elif chosen == 2:
                if self.host.get_offset_tile(self.direction, 0).is_land([Tile.COLLIDE_UNIT]):
                    self.direction = -self.direction
                else:
                    self.direction_y = 0
                    self.host.input('walk', Space(self.direction, 0))
            elif chosen == 3:
                self.direction_y = 0
                self.host.input('jump', Space(self.direction, -1))
            else:
                self.direction = -self.direction
        return 0


class Move(Task):
    def __init__(self, pilot, dist):
        super().__init__(pilot)
        self.distance = dist

    def on_set(self):
        self.pilot.priority = 4

    def is_done(self):
        orig = self.pilot.var
        if not isinstance(self.pilot.var, Space):
            self.pilot.var = self.pilot.var.pos
        dist = self.pilot.var - self.host.pos
        self.pilot.var = orig
        if self.distance >= 0:
            if dist.x <= self.distance and dist.y <= self.distance:
                return 1
        else:
            if dist.x >= -self.distance and dist.y >= -self.distance:
                return 1
        return super().is_done()

    def perform(self):
        super().perform()
        orig = self.pilot.var
        if not isinstance(self.pilot.var, Space):
            self.pilot.var = self.pilot.var.pos
        if self.distance >= 0:
            dist = self.pilot.var - self.host.pos
        else:
            dist = self.host.pos - self.pilot.var
        direction = 1 if dist.x >= 0 else -1
        if dist.y > 1 and dist.x == 0:
            land = self.host.get_offset_tile(0, 1)
            if not land.is_land([Tile.COLLIDE_TERRAIN]):
                self.host.input('use', land - self.host.pos)
        else:
            front = self.host.get_offset_tile(direction, 0)
            top = self.host.get_offset_tile(direction, -1)
            if not front.is_land(Tile.CHECK_LARGE):
                if self.host.get_offset_tile(direction, 1).is_land(self.host.standables):
                    self.host.input('walk', dist)
                elif self.host.get_offset_tile(direction, 2).is_land(self.host.standables):
                    self.host.input('walk', dist)
            elif not top.is_land(Tile.CHECK_LARGE):
                self.host.input('jump', dist)
            elif not top.is_land([Tile.COLLIDE_TERRAIN]):
                self.host.input('use', top - self.host.pos)
            elif not front.is_land([Tile.COLLIDE_TERRAIN]):
                self.host.input('use', front - self.host.pos)
        self.pilot.var = orig
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
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []
        self.result = []
        self.counter = 0
        self.heuristic_threshold = 0

    def on_set(self):
        self.pilot.priority = 4

    def is_done(self):
        orig = self.pilot.var
        if not isinstance(self.pilot.var, Space):
            self.pilot.var = self.pilot.var.pos
        r = super().is_done() or (self.host.pos - self.pilot.var).difference() <= 1
        self.pilot.var = orig
        if r:
            self.reset()
        return r

    def iterate(self, node):
        index = 0
        for k, v in enumerate(self.open):
            if v.f < node.f:
                index = k
                node = v
        self.open.pop(index)
        self.closed.append(node)
        achieved = (node.node - self.pilot.var).distance()
        if achieved < 2:
            return node
        options = self.pilot.get_routes(node.node)
        for i in options:
            pos = self.host.location.get_tile(node.node + i)
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            mod = 1 if i[1] == -1 else 0
            if conflict:
                if node.g + 1 + mod <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1 + mod
                    conflict.set_h(self.pilot.var)
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1 + mod
            new.set_h(self.pilot.var)
            new.f = new.h + new.g
            if new.h < self.heuristic_threshold:
                self.open.append(new)

    @staticmethod
    def check_loop(loop, pos):
        for i in loop:
            if i.node == pos:
                return i

    def perform(self):
        if self.result:
            orig = self.pilot.var
            if not isinstance(self.pilot.var, Space):
                self.pilot.var = self.pilot.var.pos
            dist = self.result[0] - self.host.pos
            new_dist = (self.result[len(self.result)-1] - self.pilot.var).difference()
            cur_dist = (self.host.pos - self.pilot.var).difference()
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
                if dist.x == 0:
                    self.host.input('duck', dist)
                else:
                    self.host.input('walk', dist)
            self.pilot.var = orig

    def update(self):
        orig = self.pilot.var
        if not isinstance(self.pilot.var, Space):
            self.pilot.var = self.pilot.var.pos
        for times in range(3):
            self.counter += 1
            if self.open:
                # from src.entity.Effect import Effect
                # for i in self.open:
                #     Effect.make('blood', i.node.get_center())
                done = self.iterate(self.open[0])
                if done:
                    result = [done.node]
                    while done.parent:
                        done = done.parent
                        result.insert(0, done.node)
                        if done.node == self.host.pos:
                            break
                    self.result = result
                    self.result.pop(0)
                    self.reset()
                elif self.counter > 40:
                    self.reset()
            else:
                self.reset()
        self.pilot.var = orig

    def reset(self):
        self.heuristic_threshold = (self.host.pos - self.pilot.var).distance()*3
        self.counter = 0
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []


class Pickup(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.lifetime = 4

    def on_set(self):
        self.pilot.priority = 3

    def perform(self):
        super().perform()
        if not self.host.is_armed():
            self.host.input('interact', self.host.next_target)
        else:
            self.pilot.strategize()
            self.lifetime = 0


class Attack(Task):
    def on_set(self):
        self.pilot.priority = 1

    def is_done(self):
        return super().is_done() or self.pilot.var.removed

    def perform(self):
        if self.pilot.var:
            dist = self.pilot.var.pos - self.host.pos
            if -1 <= dist.y <= 1 and -1 <= dist.x <= 1:
                self.host.input(Global.r.rand_list(self.host.action.skills + ['use']), dist)
                return 1


class Melee(Task):
    def __init__(self, pilot, special):
        super().__init__(pilot)
        self.special = special

    def on_set(self):
        self.pilot.priority = 1

    def is_done(self):
        return super().is_done() or self.pilot.var.removed

    def in_range(self, x):
        for i in self.host.weapon.range:
            if i == x:
                return 1
        return 0

    def perform_gapcloser(self, dist):
        if Global.r.rand_bool() and self.special and dist.y == 0:
            dist_x = abs(dist.x)
            if dist_x == 2 and 'lunge' in self.host.action.skills:
                self.host.input('lunge', dist)
                return 1
            elif dist_x == 2 and 'tackle' in self.host.action.skills:
                self.host.input('tackle', dist)
                return 1
            if dist_x > 2 and 'sprint' in self.host.action.skills:
                self.host.input('sprint', dist)
                return 1

    def perform_attack(self, diff):
        if 'flurry' in self.host.action.skills and Global.r.rand_bool():
            self.host.input('flurry', diff)
        else:
            self.host.input('use', diff)

    def perform(self):
        if self.pilot.var and self.host.faction != self.pilot.var.faction:
            self.pilot.strategize()
            diff = self.pilot.var.pos - self.host.pos
            if self.perform_gapcloser(diff):
                return 1
            longest_range = 0
            for i in self.host.weapon.range:
                if i > longest_range:
                    longest_range = i
            dist = round(diff.distance())
            if self.in_range(dist):
                if -1 <= diff.y <= 1:
                    self.perform_attack(diff)
                    return 1
            elif dist <= 1:
                self.host.next_target.x *= -1
                self.host.input('walk', self.host.next_target)


class Range(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.move = Move(self.pilot, -4)

    def on_set(self):
        self.pilot.priority = 1

    def perform(self):
        if self.pilot.var and self.host.faction != self.pilot.var.faction:
            diff = self.pilot.var.pos - self.host.pos
            reach = self.host.location.collide_land(self.host.pos, diff.x, diff.y,
                                                    distance=9, flag=Tile.CHECK_FIRM)
            if reach == self.pilot.var.pos:
                dist = diff.distance()
                if dist == 1 and diff.y == 0:
                    self.host.input('kick', diff)
                elif dist > 4:
                    self.host.input('use', diff)
                else:
                    self.move.perform()
                return 1


class Search(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.lifetime = 3

    def on_set(self):
        self.pilot.priority = 3

    def perform(self):
        super().perform()
        sight = self.pilot.get_sight()
        self.pilot.perceive(sight, offset=(self.host.direction * (3 - self.lifetime) * sight, 0))
        self.host.face(self.host.direction * -1)


class Hunt(Task):
    def on_set(self):
        self.pilot.priority = 1

    def is_done(self):
        return self.pilot.attack.is_done()

    def perform(self):
        super().perform()
        if not self.pilot.attack.perform():
            self.pilot.move.perform()

    def update(self):
        self.pilot.move.update()
