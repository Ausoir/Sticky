from src.game import Global


class Idle:
    def __init__(self, pilot):
        self.pilot = pilot
        self.host = self.pilot.host

    def load(self, arg):
        pass

    def record(self):
        self.host.tags.remove('tgt')

    def perform(self):
        pass

    def on_set(self):
        self.pilot.priority = 5
        self.pilot.lifetime = 100

    def update(self):
        if self.pilot.lifetime > 0:
            self.pilot.lifetime -= 1
        elif self.pilot.lifetime == 0:
            self.pilot.set_task(self.pilot.default)
            return False
        return True

    def adjust_pos(self, arg):
        pass


class TileTask(Idle):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def record(self):
        if self.target:
            host = Global.world.get_tile_true_pos(self.host.pos.x, self.host.pos.y)
            target = Global.world.get_tile_true_pos(self.target.x, self.target.y)
            target = 'x' + str(target[0] - host[0]) + 'y' + str(target[1] - host[1])
            self.host.tags.set('tgt', target)

    def load(self, arg):
        pos = arg.split('y')
        tile = self.host.pos.get_neighbor(int(pos[0][1:]), int(pos[1]))
        self.target = tile
        return self.target

    def update(self):
        if super().update():
            if not self.target:
                self.pilot.set_task(self.pilot.default)
                return False
            return True

    def adjust_pos(self, arg):
        if self.target:
            self.target = self.target.get_neighbor(arg.x, arg.y)


class TargetTask(TileTask):
    def record(self):
        if self.target:
            temp = self.target
            self.target = self.target.pos
            super().record()
            self.target = temp

    def load(self, arg):
        tile = super().load(arg)
        if tile:
            things = tile.things
            from src.entity.unit.Unit import Unit
            for i in things:
                if isinstance(i, Unit):
                    self.target = i
                    return self.target
        self.target = None

    def update(self):
        if super().update():
            if self.target.removed == 1:
                self.pilot.set_task(self.pilot.default)
                return False
            return True

    def adjust_pos(self, arg):
        pass


class Return(Idle):
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


class Path(TileTask):  # path finding A*
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
        self.chase = 11
        self.open = None
        self.closed = []
        self.closest = None
        self.result = []
        self.next_reset = 0
        self.heuristic_threshold = 0
        self.out_of_reach = False

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
            pos = node.node.get_neighbor(i[0], i[1], limit=True)
            if self.check_loop(self.closed, pos):
                continue
            conflict = self.check_loop(self.open, pos)
            if conflict:
                if node.g + 1 <= conflict.g:
                    conflict.parent = node
                    conflict.g = node.g + 1 - node.node.get_yield() + i[2]
                    conflict.set_h(self.target)
                    conflict.f = conflict.h + conflict.g
                continue
            new = Path.Node(node, pos)
            new.g = node.g + 1 - node.node.get_yield() + i[2]
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
            direction = self.host.pos.get_face(self.result[0])
            front = self.host.pos.get_cardinal(self.host.direction, 1)
            if front.get_solidity() >= self.host.collision_type and self.pilot.route.can_destroy(front) != -1:
                self.pilot.face('attack', direction)
            else:
                self.pilot.face('walk', direction)
            self.result = []
        if not self.target or (self.host.pos - self.target).difference() <= 1:
            return True

    def update(self):
        if super().update():
            if not self.result and (self.host.pos - self.target).difference() > 1:
                done = None
                if self.next_reset == 0:
                    self.reset()
                    self.next_reset = 1
                else:
                    self.next_reset += 1
                for times in range(10):
                    if self.open:
                        done = self.iterate(self.open[0])
                        if done:
                            break
                    else:
                        break
                # self.debug_trace()
                if not done and self.next_reset > self.chase:
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
            return True

    def reset(self):
        self.heuristic_threshold = (self.host.pos - self.target).distance() * 2 + 4
        self.open = [Path.Node(None, self.host.pos)]
        self.closed = []
        self.closest = self.open[0]

    def debug_trace(self):
        for draw in self.open:
            from src.entity.Particle import Particle
            Particle.make('blood', draw.node, offset=6)


class Wander(Idle):
    def __init__(self, pilot):
        super().__init__(pilot)
        self.target = None

    def on_set(self):
        super().on_set()
        self.target = None
        self.pilot.lifetime = 100
        self.pilot.priority = 4
        self.random_state()

    def random_state(self):
        rand = Global.r.rand_int(0, 3)
        self.pilot.lifetime = Global.r.rand_int(50, 200)
        if rand == 0:
            self.find_destination()
        elif rand == 1:
            self.pilot.face('walk', Global.r.rand_int(0, 3))

    def find_destination(self):
        self.target = self.host.pos
        for i in range(9):
            option = Global.r.rand_list(self.pilot.route.get(self.target))
            if option:
                self.target = self.target.get_neighbor(option[0], option[1], limit=True)

    def perform(self):
        if self.target:
            if self.pilot.is_humanoid and not self.host.weapon:
                from src.entity.unit.item.Item import Item
                for i in self.host.pos.things:
                    if isinstance(i, Item) and i != self.host and i != self.host.armor and i != self.host.headgear\
                            and i.tags.get('$', 0) > 1 and Global.r.rand_int(0, 2) == 0:
                        self.host.input('grab')
                        return
            self.pilot.move.target = self.target
            self.pilot.move.perform()

    def update(self):
        if super().update():
            self.pilot.move.target = self.target
            self.pilot.move.update()
            return True


class Attack(TargetTask):
    def on_set(self):
        super().on_set()
        self.pilot.lifetime = 500
        self.pilot.priority = 1
        if self.pilot.is_humanoid and not self.host.weapon:
            weapon = self.pilot.host.inventory.find_weapon()
            if weapon is not None:
                self.pilot.host.unsheathe(weapon)

    def update(self):
        if super().update():
            self.pilot.move.target = self.target.pos
            self.pilot.move.update()
            return True

    def perform(self):
        if self.target:
            dist = self.target.pos - self.host.pos
            diff = dist.difference()
            reach = self.host.get_skill('reach')
            attack_range = reach + self.host.get_skill('lunge') + 1
            if diff == 0:
                self.pilot.face('walk', self.target.direction + 2)
            elif diff == 1:
                if reach > 0:
                    direction = self.host.pos.get_face(self.target.pos)
                    if self.host.pos.get_cardinal(direction + 2).get_solidity() >= self.host.collision_type:
                        self.pilot.face('attack', direction)
                    else:
                        self.pilot.face('walk', direction + 2)
                else:
                    direction = self.host.pos.get_face(self.target.pos)
                    concentration = self.host.states.get('Concentration')
                    if concentration and self.host.get_skill('side step'):
                        self.pilot.face('walk', direction)
                    else:
                        self.pilot.face('attack', direction)
            elif diff <= attack_range and (dist.x == 0 or dist.y == 0) and\
                    self.host.pos.location.collide_land(self.host.pos, self.target.pos, flag=self.host.collision_type+2,
                                                        return_prev=False) == self.target.pos:
                direction = self.host.pos.get_face(self.target.pos)
                self.pilot.face('attack', direction)
            elif self.pilot.move.out_of_reach:
                self.pilot.set_task(self.pilot.move)
                self.pilot.priority = 2
                self.pilot.move.target = self.target.pos
            else:
                ability = self.host.tags.get('ab1')
                if ability and Global.r.rand_int(0, 6) == 0:
                    self.host.action.set('ability1')
                else:
                    self.pilot.move.target = self.target.pos
                    self.pilot.move.perform()


class Follow(TargetTask):
    def on_set(self):
        super().on_set()
        self.pilot.priority = 3

    def update(self):
        if not self.target:
            target = self.host.tags.get('tgt')
            if target:
                self.load(target)
            else:
                team = self.host.get_team()
                done = False
                for i in self.host.pos.get_area(3, 3):
                    if i != self.host.pos:
                        for thing in i.things:
                            if thing in team and thing.tags.get('ai') != 'ally':
                                self.target = thing
                                done = True
                                break
                    if done:
                        break
        if super().update():
            self.pilot.move.target = self.target.pos
            temp = self.pilot.move.chase
            self.pilot.move.chase = 2
            self.pilot.move.update()
            self.pilot.move.chase = temp
            return True

    def perform(self):
        if self.target:
            self.pilot.move.target = self.target.pos
            self.pilot.move.perform()


class Guard(Path):
    def update(self):
        if not self.target:
            guard = self.host.tags.get('guard')
            host_pos = Global.world.get_tile_true_pos(self.host.pos.x, self.host.pos.y)
            if guard:
                pos = guard[1:].split('y')
                tile = self.host.pos.get_neighbor(int(pos[0]) - host_pos[0], int(pos[1]) - host_pos[1], limit=True)
            else:
                self.host.tags.set('guard', 'x' + str(host_pos[0]) + 'y' + str(host_pos[1]))
                tile = self.host.pos
            self.target = tile
        return super().update()
