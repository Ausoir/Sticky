from src.entity.unit.ai.Task import *
from src.map.Tile import Tile


class Pilot:
    def __init__(self, host):
        self.host = host
        self.default = None
        self.move = None
        self.attack = None
        self.route = None
        self.task = None
        self.priority = 5
        self.is_humanoid = False
        self.task_lifetime = 500

    def record(self):
        if self.host.tags.get('ai'):
            if self.task != self.default and self.task.__class__ != Return:
                self.host.tags.set('task', self.task.__class__.__name__)
            self.task.record()

    def load(self, arg):
        if arg == 'guard':
            self.default = Guard(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host, False)
        elif arg == 'wander':
            self.default = Wander(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host, True)
        elif arg == 'ally':
            self.default = Follow(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host, False)
        else:
            return
        self.host.tags.set('ai', arg)
        tgt = self.host.tags.get('tgt')
        if tgt is not None:
            self.retarget(tgt)
        else:
            self.set_task(self.default)

    def retarget(self, target):
        self.set_task(Return(self, target))

    def update(self):
        if self.task.update() and self.host.action.delay == 0:
            self.act()

    def set_task(self, task):
        task.on_set()
        self.task = task
        if self.priority == 1:
            interaction = self.host.tags.get('#')
            if interaction and interaction != 'busy' and interaction != '>menu>order':
                self.host.tags.set('!#', interaction)
                self.host.tags.set('#', 'busy')
        else:
            interaction = self.host.tags.remove('!#')
            if interaction:
                self.host.tags.set('#', interaction)

    def act(self):
        if self.priority > 1:
            enemies = self.host.get_team(ally=False)
            targets = self.perceive(enemies)
            if targets:
                self.spot_enemy(targets)
        self.task.perform()

    def hit(self, hitter):
        ai = self.host.tags.get('ai')
        if ai and hitter is not None and hitter != self.host:
            if ai != 'ally' or self.host.tags.get('team', 0) != hitter.tags.get('team', 0):
                self.set_task(self.attack)
                self.task.target = hitter
                if not self.host.tags.get('deaf'):
                    allies = self.host.get_team(ally=True)
                    for ally in allies:
                        distance = (ally.pos - self.host.pos).difference()
                        if distance <= 9 and ally.tags.get('ai') and ally.pilot.priority >= 2:
                            if Global.world.location.collide_land(self.host.pos, ally.pos, ally.sight, prev=False)\
                                    == ally.pos:
                                ally.pilot.set_task(ally.pilot.attack)
                                ally.pilot.task.target = hitter

    def perceive(self, enemies):
        perceived = []
        night_vision = self.host.get_skill('nocturnal')
        psychic = self.host.get_skill('psychic') or self.host.states.get('Vision')
        vision = self.host.tags.get('sth', 0)
        front = self.host.pos.get_cardinal(self.host.direction)
        for thing in enemies:
            if self.host.is_facing(thing.pos):
                diff_x = abs(thing.pos.x - self.host.pos.x)
                diff_y = abs(thing.pos.y - self.host.pos.y)
                if psychic:
                    in_range = True
                else:
                    s = thing.tags.get('sth', 0) + 1
                    if thing.pos == front:
                        s -= 4
                    elif s >= 1:
                        s = max(1, s - vision - night_vision)
                    if thing.pos.light or night_vision:
                        in_range = diff_x * s <= Global.map_view.sight_range and\
                                   diff_y * s <= Global.map_view.sight_range_y
                    else:
                        in_range = diff_x <= 4 - s and diff_y <= 3 - s
                if in_range:
                    perceived.append(thing)
        return perceived

    def hear(self, pos):
        if self.host.tags.get('ai'):
            if self.priority > 3:
                if not self.host.tags.get('deaf'):
                    if (pos - self.host.pos).difference() >= 1:
                        self.face('idle', self.host.pos.get_face(pos))
                        seen = Global.world.location.collide_land(self.host.pos, pos, self.host.sight, prev=False)
                        if seen == pos:
                            units = []
                            from src.entity.unit.Unit import Unit
                            for i in pos.things:
                                if isinstance(i, Unit):
                                    units.append(i)
                            self.perceive(units)
                        else:
                            self.move.target = pos
                            self.set_task(self.move)

    def lose(self, target):
        if self.task.__class__.__name__ == 'Attack' and self.task.target == target:
            self.move.target = self.task.target.pos
            self.set_task(self.move)

    def prioritize(self, targets):
        nearest_dist = 99
        nearest = None
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                nearest_dist = t
                nearest = i
        return nearest

    def spot_enemy(self, targets):
        valids = []
        for thing in targets:
            seen = Global.world.location.collide_land(self.host.pos, thing.pos, self.host.sight, distance=13)
            if seen == thing.pos:
                valids.append(thing)
        if valids:
            var = self.prioritize(valids)
            if var:
                self.set_task(self.attack)
                self.task.target = var
                if not self.host.tags.get('deaf'):
                    from src.entity.Particle import Particle
                    Particle.make('shout', self.host.pos)
                    Global.world.location.sound.register(self.host.pos, 9)

    def face(self, action, direction):
        direction = direction % 4
        if self.host.action.delay == 0:
            if self.host.direction != direction:
                if direction == 0:
                    self.host.input('down')
                elif direction == 1:
                    self.host.input('left')
                elif direction == 2:
                    self.host.input('up')
                elif direction == 3:
                    self.host.input('right')
            else:
                self.host.input(action)


class Routes:
    def __init__(self, host, destroy):
        self.host = host
        if host.get_skill('reach'):
            self.destroy = False
        else:
            self.destroy = destroy

    def can_destroy(self, tile):
        if not self.destroy:
            if tile.get_solidity() >= self.host.collision_type:
                return -1
            else:
                return 0
        weight = 0
        for i in tile.things:
            if i.obstruct_type >= self.host.collision_type:
                hp = i.tags.get('p')
                if not hp or self.host.get_damage() <= i.tags.get('def', 0)\
                        or i.tags.get('team', 0) == self.host.tags.get('team', 0):
                    return -1
                else:
                    weight += hp
        if tile.get_yield() == -10 and self.host.collision_type <= Tile.COLLIDE_TERRAIN:
            if self.host.get_damage() > tile.get_hardness() and self.host.get_skill('destroy'):
                weight += 3
            else:
                return -1
        elif tile.get_yield() == -9 and self.host.collision_type <= Tile.COLLIDE_WINDOW:
            return -1
        return weight

    def get(self, pos):
        options = []
        left = pos.get_neighbor(-1, 0)
        right = pos.get_neighbor(1, 0)
        down = pos.get_neighbor(0, 1)
        up = pos.get_neighbor(0, -1)
        if up:
            weight = self.can_destroy(up)
            if weight != -1:
                options.append((0, -1, weight))
        if right:
            weight = self.can_destroy(right)
            if weight != -1:
                options.append((1, 0, weight))
        if left:
            weight = self.can_destroy(left)
            if weight != -1:
                options.append((-1, 0, weight))
        if down:
            weight = self.can_destroy(down)
            if weight != -1:
                options.append((0, 1, weight))
        return options
