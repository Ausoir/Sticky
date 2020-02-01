from src.game import Global


class Task:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host
        self.lifetime = 0

    def __str__(self):
        return self.__class__.__name__

    def perform(self):
        pass

    def on_set(self):
        pass

    def update(self):
        self.lifetime += 1


class TargetTask(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def update(self):
        super().update()
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
        self.open = None
        self.closed = []
        self.closest = None
        self.result = []
        self.next_reset = 0
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
        if achieved < (self.closest.node - self.target).difference():
            self.closest = node
        options = self.pilot.path.get(node.node)
        for i in options:
            pos = self.host.location.get_tile(node.node + i)
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            if conflict:
                if node.g + 1 <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1
                    conflict.set_h(self.target)
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1
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
            cur_dist = (self.host.pos - self.target).difference()
            if cur_dist <= 1:
                pass
            else:
                self.host.face_toward(self.result[0])
                self.host.input('walk')
            self.result = []

    def update(self):
        super().update()
        if not self.result and (self.host.pos - self.target).difference() > 1:
            done = None
            if self.next_reset == 0:
                self.reset()
                self.next_reset = 1
            else:
                self.next_reset += 1
            for times in range(12):
                if self.open:
                    done = self.iterate(self.open[0])
                    if done:
                        break
                else:
                    break
            # self.debug_trace()
            if not done and self.next_reset > 9:
                done = self.closest
            if done:
                self.next_reset = 0
                self.result = [done.node]
                while done.parent:
                    done = done.parent
                    if done.node == self.host.pos:
                        break
                    self.result.insert(0, done.node)

    def reset(self):
        self.heuristic_threshold = (self.host.pos - self.target).distance() * 2 + 4
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []
        self.closest = self.open[0]

    def debug_trace(self):
        for draw in self.open:
            from src.entity.Particle import Particle
            Particle.make('blood', draw.node.get_center() + Global.r.rand_int(-15, 15))


class Attack(TargetTask):
    def on_set(self):
        self.pilot.priority = 1

    def update(self):
        super().update()
        if self.target and not self.target.removed:
            self.pilot.move.target = self.target.pos
            self.pilot.move.update()
        else:
            self.pilot.set_task()

    def perform(self):
        if self.target:
            dist = self.target.pos - self.host.pos
            if dist.difference() == 1:
                self.host.face_toward(self.target.pos)
                self.host.input(Global.r.rand_list(self.host.action.skills + ['use']))
                return True
            self.pilot.move.target = self.target.pos
            self.pilot.move.perform()


class Follow(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def on_set(self):
        self.pilot.priority = 3

    def update(self):
        super().update()
        if not self.target:
            if self.pilot.var['ally'] == Global.player.character.id:
                self.target = Global.player.character
            else:
                for i in self.host.location.record:
                    if i.id == self.pilot.var['ally']:
                        self.target = i
                        break
        else:
            self.pilot.move.target = self.target.pos
            self.pilot.move.update()

    def perform(self):
        if self.target:
            self.pilot.move.target = self.target.pos
            self.pilot.move.perform()
