from src.entity.Space import Space
from src.game import Global
from src.map.Tile import Tile


class Task:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host
        self.lifetime = 80

    def __str__(self):
        return self.__class__.__name__

    def perform(self):
        pass

    def on_set(self):
        pass

    def update(self):
        self.lifetime -= 1
        if self.lifetime == 0:
            self.pilot.set_task(self.pilot.var['def'])


class TargetTask(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def update(self):
        if not self.target:
            if self.pilot.var['var'] == Global.player.character.id:
                self.target = Global.player.character
            else:
                for i in self.host.location.record:
                    if i.id == self.pilot.var['var']:
                        self.target = i
                        break


class Idle(Task):
    def on_set(self):
        self.pilot.priority = 5

    def perform(self):
        super().perform()
        self.pilot.var['now'] = self.pilot.var['def']


class Post(Task):
    def on_set(self):
        self.pilot.priority = 4

    def perform(self):
        super().perform()
        if not self.lifetime % 20:
            self.host.face(self.host.direction * -1)


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
        if not self.stop and Global.player.is_daytime():
            routes = self.pilot.var['path'].get(self.host.pos)
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
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = self.host.pos
        self.distance = 1

    def update(self):
        super().update()
        dist = (self.target - self.host.pos).difference()
        if self.distance >= 0:
            if dist <= self.distance:
                return True
        else:
            if dist >= -self.distance:
                return True

    def perform(self):
        super().perform()
        self.host.face_toward(self.target)
        front = self.host.get_front_tile(self.host.direction)
        if not front.is_land(Tile.CHECK_LARGE):
            self.host.input('walk')


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
        self.target = self.host.pos
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []
        self.result = []
        self.counter = 0
        self.heuristic_threshold = 0

    def iterate(self, node):
        index = 0
        for k, v in enumerate(self.open):
            if v.f < node.f:
                index = k
                node = v
        self.open.pop(index)
        self.closed.append(node)
        achieved = (node.node - self.target).difference()
        if achieved <= 1:
            return node
        options = self.pilot.var['path'].get(node.node)
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
                    conflict.set_h(self.target)
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1 + mod
            new.set_h(self.target)
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
            dist = (self.result[0] - self.host.pos).difference()
            new_dist = (self.result[len(self.result)-1] - self.target).difference()
            cur_dist = (self.host.pos - self.target).difference()
            if cur_dist <= 1:
                pass
            elif cur_dist <= new_dist:
                self.result = []
                self.reset()
            elif dist == 0:
                self.result.pop(0)
                self.perform()
            elif dist > 8:
                self.result = []
                self.reset()
            else:
                self.host.face_toward(self.result[0])
                self.host.input('walk')

    def update(self):
        super().update()
        if (self.host.pos - self.target).difference() > 1:
            from src.entity.Particle import Particle
            for i in self.open:
                Particle.make('blood', i.node.get_center() + Global.r.rand_int(-15, 15))
            for times in range(3):
                self.counter += 1
                if self.open:
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
        else:
            self.reset()

    def reset(self):
        self.heuristic_threshold = (self.host.pos - self.target).distance()*3
        self.counter = 0
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []


class Attack(TargetTask):
    def on_set(self):
        self.pilot.priority = 1

    def update(self):
        super().update()
        if self.target and not self.target.removed:
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].update()
        else:
            self.pilot.set_task()

    def perform(self):
        if self.target:
            dist = self.target.pos - self.host.pos
            if dist.difference() == 1:
                self.host.face_toward(self.target.pos)
                self.host.input(Global.r.rand_list(self.host.action.skills + ['use']))
                return True
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].perform()


class Martial(Attack):
    def on_set(self):
        self.pilot.priority = 1

    def in_range(self, x):
        return x <= self.host.weapon.reach

    def perform_gapcloser(self, dist):
        if Global.r.rand_bool() and dist.y == 0:
            dist_x = abs(dist.x)
            if dist_x == 1 + self.host.weapon.reach and 'lunge' in self.host.action.skills:
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
        if self.target:
            diff = self.target.pos - self.host.pos
            if self.perform_gapcloser(diff):
                return True
            dist = round(diff.distance())
            if self.in_range(dist):
                if -1 <= diff.y <= 1:
                    self.perform_attack(diff)
                    return True
            elif dist <= 1:
                self.host.next_target.x *= -1
                self.host.input('walk', self.host.next_target)
                return True
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].perform()


class Range(Attack):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.move = Move(self.pilot)
        self.move.distance = -3

    def on_set(self):
        self.pilot.priority = 1

    def perform(self):
        if self.target:
            if not self.host.weapon.is_reloaded():
                self.host.input('interact', self.host.next_target)
            else:
                diff = self.target.pos - self.host.pos
                reach = self.host.location.collide_land(self.host.pos, diff.x, diff.y,
                                                        distance=9, flag=Tile.CHECK_FIRM)
                if reach == self.target.pos:
                    dist = diff.distance()
                    if dist > 4:
                        self.host.input('use', diff)
                    else:
                        self.move.target = self.target.pos
                        self.move.perform()
                        if self.host.next_action == 'idle':
                            self.host.input('use', diff)
                    return True
                else:
                    self.move.target = self.target.pos
                    self.pilot.var['move'].perform()


class Magic(Attack):
    def on_set(self):
        self.pilot.priority = 1

    def perform_gapcloser(self, dist):
        if Global.r.rand_bool() and dist.y == 0:
            dist_x = abs(dist.x)
            if dist_x == 1 + self.host.weapon.reach and 'lunge' in self.host.action.skills:
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
        if self.target:
            diff = self.target.pos - self.host.pos
            if self.perform_gapcloser(diff):
                return True
            dist = round(diff.distance())
            if dist < 6:
                if -1 <= diff.y <= 1:
                    self.perform_attack(diff)
                    return True
            elif dist <= 1:
                self.host.next_target.x *= -1
                self.host.input('walk', self.host.next_target)
                return True
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].perform()


class Melee(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.attack = None
        self.strategize()

    def on_set(self):
        self.pilot.priority = 1

    def update(self):
        self.attack.update()

    def perform(self):
        self.strategize()
        self.attack.perform()

    def strategize(self):
        from src.entity.unit.item.Spell import Spell
        from src.entity.Other import Ballistic
        if isinstance(self.host.weapon, Ballistic):
            if self.attack.__class__ != Range:
                self.attack = Range(self.pilot)
        elif isinstance(self.host.weapon, Spell):
            if self.attack.__class__ != Magic:
                self.attack = Magic(self.pilot)
        else:
            if self.attack.__class__ != Martial:
                self.attack = Martial(self.pilot)


class Follow(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def on_set(self):
        self.pilot.priority = 3

    def update(self):
        if not self.target:
            if self.pilot.var['ally'] == Global.player.character.id:
                self.target = Global.player.character
            else:
                for i in self.host.location.record:
                    if i.id == self.pilot.var['ally']:
                        self.target = i
                        break
        else:
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].update()

    def perform(self):
        if self.target:
            self.pilot.var['move'].target = self.target.pos
            self.pilot.var['move'].perform()


class Search(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.lifetime = 4

    def on_set(self):
        self.pilot.priority = 3

    def perform(self):
        super().perform()
        sight = self.pilot.get_sight()
        self.host.face(self.host.direction * -1)
        self.pilot.perceive(sight, offset=(self.host.direction * (3 - self.lifetime) * sight, 0))


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
