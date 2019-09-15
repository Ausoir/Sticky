from src.entity.unit.Unit import Unit
from src.entity.unit.ai.Task import *
from src.game.Turn import Turn


class Manual:
    def __init__(self, host, task, var):
        self.host = host
        from src.entity.unit.ai import Task as AllTask
        self.task = getattr(AllTask, task)(self)
        if var != -1:
            if isinstance(var, list):
                self.var = self.host.location.get_tile(var)
            else:
                self.var = var
                Turn.add(self.turn)
        else:
            self.var = None

    def __str__(self):
        task_str = str(self.task.__class__.__name__)
        return '[' + self.__class__.__name__ + ',' + task_str + ',' + self.get_var_string() + ']'

    def get_var_string(self):
        if self.var:
            from src.entity.Object import Object
            if isinstance(self.var, Object):
                return str(self.var.id)
            return str(self.var)
        return '-1'

    def turn(self):
        if self.var == Global.player.character.id:
            self.var = Global.player.character
            return
        for i in self.host.location.record:
            if i.id == self.var:
                self.var = i
                break

    def add_task(self, task):
        task.next = self.task
        self.task = task
        self.task.on_set()

    def hit(self):
        pass

    def update(self):
        pass

    def hear(self, pos):
        pass


class Basic(Manual):
    def __init__(self, host, task, var):
        super().__init__(host, task, var)
        self.priority = 5
        self.move = Move(self, 1)
        self.attack = Attack(self)


class Guard(Basic):
    def __init__(self, host, task, var):
        super().__init__(host, task, var)

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            if self.priority == 5:
                self.perceive()
            if self.task.is_done() and self.task.next:
                self.task = self.task.next
                self.task.on_set()
            self.task.perform()

    def perceive(self):
        aoe = self.host.location.get_area(self.host.pos, 1, 1)
        for i in aoe:
            for thing in i.things:
                if thing != self.host and isinstance(thing, Unit) and self.host.faction != thing.faction:
                    self.priority = 1
                    self.add_task(self.attack)
                    self.var = thing
                    return


class Pilot(Basic):
    def __init__(self, host, task, var):
        super().__init__(host, task, var)
        self.priority = 5
        self.hunt = Hunt(self)
        self.hunt.move = self.move
        self.hunt.attack = Attack(self)

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            sight = self.get_sight()
            if self.priority > 2:
                targets = self.perceive(sight, offset=(sight * self.host.direction, 0))
                if targets:
                    self.spot_enemy(targets)
            if self.priority > 4:
                if self.host.attributes.gene % 5 == 0:
                    self.task = Wander(self)
            if self.task.is_done() and self.task.next:
                self.task = self.task.next
                self.task.on_set()
            self.task.perform()

    def get_sight(self):
        return max(self.host.attributes.intelligence, int(self.host.location.sight_range / 2))

    def hit(self):
        if self.priority > 1:
            self.priority = 3
            self.add_task(Search(self))
        else:
            targets = self.perceive(6)
            if targets:
                self.spot_enemy(targets)

    def perceive(self, sight, offset=(0, 0)):
        perceived = []
        aoe = self.host.location.get_area(self.host.pos + (offset[0], offset[1]), sight, int(sight/2))
        for i in aoe:
            if i.light or abs(i.x - self.host.pos.x) < self.host.location.view_range:
                for thing in i.things:
                    if thing != self.host:
                        perceived.append(thing)
        targets = []
        host_pos = self.host.pos.get_center().to_list()
        for thing in perceived:
            seen = thing.pos == self.host.pos
            if not seen:
                to = (thing.pos - self.host.pos).to_list()
                seen = self.host.location.collide_sight(host_pos, to)
            if seen:
                if isinstance(thing, Unit):
                    if self.host.faction != thing.faction:
                        targets.append(thing)
        return targets

    def hear(self, pos):
        if self.priority > 3:
            self.var = pos.to_space()
            self.add_task(self.move)

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = targets[0]
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                nearest_dist = t
                nearest = i
        return nearest

    def spot_enemy(self, targets):
        self.priority = 1
        self.var = self.prioritize(targets)
        self.add_task(self.hunt)
        from src.entity.Effect import Effect
        Effect.make('shout', self.host.vec)
        self.host.location.sound.register(self.host.pos, 16)

    def get_routes(self, pos):
        options = []
        right = self.host.location.get_tile(pos + (1, 0))
        upright = self.host.location.get_tile(pos + (1, -1))
        left = self.host.location.get_tile(pos + (-1, 0))
        upleft = self.host.location.get_tile(pos + (-1, -1))
        ground = self.host.location.get_tile(pos + (0, 1))
        air = self.host.location.get_tile(pos + (0, -1))
        if not air.is_land(Tile.CHECK_FIRM) and pos.is_climbable():
            options.append((0, -1))
        if not right.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (1, 1)).is_land(self.host.standables):
                options.append((1, 0))
            elif self.host.location.get_tile(pos + (1, 2)).is_land(self.host.standables):
                options.append((1, 1))
        if not upright.is_land(Tile.CHECK_FIRM) and right.is_land(self.host.standables):
            options.append((1, -1))
        if not left.is_land(Tile.CHECK_FIRM):
            if self.host.location.get_tile(pos + (-1, 1)).is_land(self.host.standables):
                options.append((-1, 0))
            elif self.host.location.get_tile(pos + (-1, 2)).is_land(self.host.standables):
                options.append((-1, 1))
        if not upleft.is_land(Tile.CHECK_FIRM) and left.is_land(self.host.standables):
            options.append((-1, -1))
        if not ground.is_land(Tile.CHECK_FIRM) and ground.is_climbable():
            options.append((0, 1))
        return options


class Sentient(Pilot):
    def __init__(self, host, task, var):
        super().__init__(host, task, var)
        self.move = Path(self)
        self.hunt.move = self.move
        self.hunt.attack = Melee(self, 1)

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            if not self.dodge():
                sight = self.get_sight()
                if self.priority > 2:
                    targets = self.perceive(sight, offset=(sight * self.host.direction, 0))
                    if targets:
                        self.spot_enemy(targets)
                if self.priority > 4:
                    if self.host.attributes.gene % 5 == 0:
                        self.task = Wander(self)
                if self.task.is_done() and self.task.next:
                    self.task = self.task.next
                    self.task.on_set()
                self.task.perform()

    def dodge(self):
        if 'block' in self.host.action.skills:
            for i in self.host.location.attack.registry:
                if i[2] == self.host.pos:
                    self.host.input('block', None)
                    return True

    def strategize(self):
        if self.host.weapon.name == 'Bow':
            self.hunt.attack = Range(self)
        else:
            self.hunt.attack = Melee(self, 1)

    def hit(self):
        if self.priority > 1:
            if self.var:
                targets = self.perceive(6)
                if not targets:
                    self.add_task(self.hunt)
            self.priority = 3
            self.add_task(Search(self))
            self.var = Global.player.character
        else:
            targets = self.perceive(6)
            if targets:
                self.spot_enemy(targets)


class Ally(Sentient):
    def __init__(self, host, task, var):
        super().__init__(host, task, var)
        self.move = Path(self)
        self.task = self.move
        self.hunt.move = self.move
        self.hunt.attack = Melee(self, 1)

    def update(self):
        if self.priority > 3:
            self.task = self.move
            self.var = Global.player.character.pos.to_space()
        self.task.update()
        if self.host.delay == 0:
            if not self.dodge():
                if self.priority > 2:
                    targets = self.perceive(4)
                    if targets:
                        self.spot_enemy(targets)
                if self.task.is_done() and self.task.next:
                    self.task = self.task.next
                    self.task.on_set()
                self.task.perform()

    def hit(self):
        if self.priority > 1:
            self.priority = 3
            self.add_task(Search(self))
        else:
            targets = self.perceive(6)
            if targets:
                self.spot_enemy(targets)
