from src.game import Global


class Task:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host
        self.lifetime = -1

    def load(self, arg):
        pass

    def record(self):
        self.host.tags.remove('tgt')

    def perform(self):
        pass

    def on_set(self):
        self.lifetime = -1

    def on_finish(self):
        self.pilot.set_task(self.pilot.default)

    def update(self):
        if self.lifetime > 0:
            self.lifetime -= 1
        elif self.lifetime == 0:
            self.pilot.set_task(self.pilot.default)


class TargetTask(Task):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def record(self):
        if self.target:
            target = 'x' + str(self.target.pos.x) + 'y' + str(self.target.pos.y)
            self.host.tags.set('tgt', target)

    def load(self, arg):
        pos = arg.split('y')
        self.target = self.host.location.population.get_from_pos(int(pos[0][1:]), int(pos[1]))


class Return(Task):
    def __init__(self, pilot, target):
        super().__init__(pilot)
        self.target = target
        self.task = self.host.tags.remove('task')

    def update(self):
        if self.task:
            # noinspection PyUnresolvedReferences
            import src.entity.unit.ai.Task as Behavior
            self.pilot.set_task(getattr(Behavior, self.task)(self.pilot))
        else:
            self.pilot.set_task(self.pilot.default)
        self.pilot.task.load(self.target)


class Idle(Task):
    def on_set(self):
        super().on_set()
        self.pilot.priority = 5


class Wander(Idle):
    class Node:
        def __init__(self, parent, node):
            self.parent = parent
            self.node = node
            self.g = 0

    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None
        self.open = None
        self.closed = []
        self.result = []
        self.closest = None
        self.next_reset = 0
        self.state = 0

    def on_set(self):
        super().on_set()
        self.lifetime = 120
        self.pilot.priority = 4
        self.state = 0

    def iterate(self, node):
        index = 0
        for k, v in enumerate(self.open):
            if v.g < node.g:
                index = k
                node = v
        self.open.pop(index)
        self.closed.append(node)
        options = self.pilot.route.get(node.node)
        for i in options:
            pos = node.node.get_neighbor(i[0], i[1])
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            if conflict:
                if node.g + 1 <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1
                continue
            new = Wander.Node(node, pos)
            new.g = node.g + 1
            self.open.append(new)

    @staticmethod
    def check_loop(loop, pos):
        for i in loop:
            if i.node == pos:
                return i

    def random_state(self):
        rand = Global.r.rand_int(0, 5)
        if rand == 0:
            self.lifetime = 400
            self.state = 1
            self.reset()
            self.target = None
        elif rand < 3:
            self.host.face(Global.r.rand_int(0, 3))
            self.state = 0
        else:
            self.state = 0

    def perform(self):
        if self.state == 0:
            if self.lifetime % 20 == 0:
                self.random_state()
        elif self.state == 1:
            if self.result:
                self.host.face_toward(self.result[0])
                self.host.input('walk')
                self.result = []

    def update(self):
        super().update()
        if self.state == 1:
            self.update_wander()

    def update_wander(self):
        if not self.result:
            if self.next_reset == 0:
                self.reset()
                self.next_reset = 1
            else:
                self.next_reset += 1
            for times in range(5):
                if self.open:
                    self.iterate(self.open[0])
                else:
                    self.next_reset = 0
                    return
            # self.debug_trace()
            if self.next_reset > 13:
                if not self.target:
                    self.target = Global.r.rand_list(self.open)
                elif self.host.pos == self.target.node:
                    self.state = 0
                self.next_reset = 0
                self.result = [self.target.node]
                done = self.target
                while done.parent:
                    done = done.parent
                    if done.node == self.host.pos:
                        break
                    self.result.insert(0, done.node)

    def reset(self):
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []
        self.closest = self.open[0]

    def debug_trace(self):
        for draw in self.open:
            from src.entity.Particle import Particle
            Particle.make('blood', draw.node, offset=6)
        if self.target:
            from src.entity.Particle import Particle
            Particle.make('barrier', self.target.node, offset=6)


class Path(Task):  # path finding A*
    chase = 14

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
        self.out_of_reach = False

    def load(self, arg):
        ints = arg[1:].split('y')
        self.target = self.host.location.get_tile(int(ints[0]), int(ints[1]))

    def record(self):
        self.host.tags.set('tgt', 'x' + str(self.target.x) + 'y' + str(self.target.y))

    def on_set(self):
        super().on_set()
        self.out_of_reach = False

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
        options = self.pilot.route.get(node.node)
        for i in options:
            pos = node.node.get_neighbor(i[0], i[1])
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            if conflict:
                if node.g + 1 <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1 - node.node.speed + i[2]
                    conflict.set_h(self.target)
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1 - node.node.speed + i[2]
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
            self.host.face_toward(self.result[0])
            front = self.host.pos.get_cardinal(self.host.direction, 1)
            if front.is_land(self.host.collision_type) and self.pilot.route.can_destroy(front) != -1:
                self.host.input('attack')
            else:
                self.host.input('walk')
            self.result = []
        if (self.host.pos - self.target).difference() <= 1:
            return True

    def update(self):
        super().update()
        if not self.result and (self.host.pos - self.target).difference() > 1:
            done = None
            if self.next_reset == 0:
                self.reset()
                self.next_reset = 1
            else:
                self.next_reset += 1
            for times in range(7):
                if self.open:
                    done = self.iterate(self.open[0])
                    if done:
                        break
                else:
                    break
            # self.debug_trace()
            if not done and self.next_reset > Path.chase:
                self.out_of_reach = True
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
            Particle.make('blood', draw.node, offset=6)


class Attack(TargetTask):
    def on_set(self):
        super().on_set()
        self.pilot.priority = 1
        if self.pilot.is_humanoid:
            weapon = self.pilot.host.inventory.find_weapon()
            if weapon is not None:
                self.pilot.host.unsheathe(weapon)

    def update(self):
        super().update()
        if self.target and self.target.removed == 0 and self.target.tags.get('p', -1) >= 0:
            self.pilot.move.target = self.target.pos
            self.pilot.move.update()
        else:
            self.pilot.set_task(self.pilot.default)

    def perform(self):
        if self.target:
            dist = self.target.pos - self.host.pos
            diff = dist.difference()
            if diff == 0:
                self.host.face(self.target.direction + 2)
                self.host.input('walk')
            elif diff == 1:
                self.host.face_toward(self.target.pos)
                concentration = self.host.states.get('Concentration')
                if concentration and self.host.get_skill('side step'):
                    self.host.input('walk')
                else:
                    self.host.input('attack')
            elif self.pilot.move.out_of_reach:
                self.pilot.set_task(self.pilot.move)
                self.pilot.priority = 3
                self.pilot.move.target = self.target.pos
            else:
                self.pilot.move.target = self.target.pos
                self.pilot.move.perform()


class Follow(TargetTask):
    def on_set(self):
        super().on_set()
        self.pilot.priority = 3

    def update(self):
        super().update()
        if not self.target:
            target = self.host.tags.get('tgt')
            if target is None:
                team = self.host.get_team()
                done = False
                for i in self.host.pos.get_area(3, 3):
                    if i != self.host.pos:
                        for thing in i.things:
                            if thing in team and thing.tags.get('ai') != 'ally':
                                target = 'x' + str(i.x) + 'y' + str(i.y)
                                done = True
                                break
                    if done:
                        break
            if target is not None:
                self.load(target)
        if self.target and self.target.removed == 0:
            self.pilot.move.target = self.target.pos
            self.pilot.move.update()
        else:
            self.pilot.set_task(self.pilot.default)

    def perform(self):
        if self.target:
            if self.pilot.move.out_of_reach:
                self.pilot.set_task(self.pilot.move)
                self.pilot.priority = 3
                self.pilot.move.target = self.target.pos
            else:
                self.pilot.move.target = self.target.pos
                self.pilot.move.perform()
