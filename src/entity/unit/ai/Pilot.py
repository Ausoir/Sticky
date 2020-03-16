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

    def record(self):
        if self.host.tags.get('ai'):
            if self.task != self.default and self.task.__class__ != Return:
                self.host.tags.set('task', self.task.__class__.__name__, add=True)
            else:
                self.host.tags.remove('task')
            self.task.record()

    def load(self, arg):
        if arg == 'guard':
            self.default = Idle(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host.collision_type)
        elif arg == 'wander':
            self.default = Wander(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host.collision_type)
        elif arg == 'ally':
            self.default = Follow(self)
            self.move = Path(self)
            self.attack = Attack(self)
            self.route = Routes(self.host.collision_type)
        elif arg == 'crusher':
            self.default = Follow(self)
            self.move = Path(self)
            self.attack = Attack(self)
            cols = filter(lambda x: x != Tile.COLLIDE_TERRAIN, self.host.collision_type)
            self.route = Routes(list(cols))
        else:
            return
        tgt = self.host.tags.get('tgt')
        if tgt:
            self.set_task(Return(self, tgt))
        else:
            self.set_task(self.default)

    def update(self):
        self.task.update()
        if self.host.action.delay == 0:
            self.act()

    def set_task(self, task):
        task.on_set()
        self.task = task

    def act(self):
        if self.priority > 2:
            enemies = self.host.get_team(ally=False)
            targets = self.perceive(enemies)
            if targets:
                self.spot_enemy(targets)
        if self.task.perform():
            self.task.on_finish()

    def hit(self, hitter):
        if self.host.tags.get('ai'):
            from src.entity.unit.item.Item import Item
            from src.entity.Prop import Prop
            if isinstance(hitter, Prop):
                if isinstance(hitter, Item) and hitter.host:
                    hitter = hitter.host
                if hitter != self.host:
                    self.set_task(self.attack)
                    self.task.target = hitter

    def perceive(self, enemies):
        perceived = []
        for thing in enemies:
            diff_x = abs(thing.pos.x - self.host.pos.x)
            diff_y = abs(thing.pos.y - self.host.pos.y)
            if self.host.is_facing(thing.pos):
                s = thing.stealth
                if thing.pos.light:
                    in_range = diff_x <= Global.map_view.sight_range - s and diff_y <= Global.map_view.sight_range_y - s
                else:
                    in_range = diff_x <= Global.map_view.view_range - s and diff_y <= Global.map_view.view_range_y - s
                if in_range:
                    perceived.append(thing)
        return perceived

    def hear(self, pos):
        if self.host.tags.get('ai'):
            if self.priority > 3:
                if not self.host.tags.get('deaf'):
                    if (pos - self.host.pos).difference() > 1:
                        self.host.face_toward(pos)
                        seen = self.host.location.collide_land(self.host.pos, pos, self.host.sight)
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
        if self.task.target == target:
            seen = self.host.location.collide_land(self.host.pos, self.task.target.pos, self.host.sight)
            if seen != target.pos:
                self.move.target = self.task.target.pos
                self.set_task(self.move)

    def prioritize(self, targets):
        nearest_dist = 10
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
            seen = self.host.location.collide_land(self.host.pos, thing.pos, self.host.sight)
            if seen == thing.pos:
                valids.append(thing)
        if valids:
            var = self.prioritize(valids)
            if var:
                self.set_task(self.attack)
                self.task.target = var
                if not self.host.tags.get('deaf'):
                    from src.entity.Particle import Particle
                    Particle.make('shout', self.host.vec)
                    self.host.location.sound.register(self.host.pos, 9)

    def can_destroy(self, tile):
        from src.entity.unit.Unit import Unit
        for i in tile.things:
            if isinstance(i, Unit) and self.host in i.get_team():
                return False
            elif i.obstruct_type in self.host.collision_type and self.host.get_damage() < i.tags.get_material_defense():
                return False
        if tile.is_land([Tile.COLLIDE_TERRAIN]):
            return not self.host.get_skill('crush') or self.host.get_damage() < 7
        return True


class Routes:
    def __init__(self, col):
        self.collision = col

    def get(self, pos):
        options = []
        left = pos.get_neighbor(-1, 0)
        right = pos.get_neighbor(1, 0)
        down = pos.get_neighbor(0, 1)
        up = pos.get_neighbor(0, -1)
        if up and not up.is_land(self.collision):
            options.append((0, -1))
        if right and not right.is_land(self.collision):
            options.append((1, 0))
        if left and not left.is_land(self.collision):
            options.append((-1, 0))
        if down and not down.is_land(self.collision):
            options.append((0, 1))
        return options
