from src.entity.unit.ai.Pilot import Pilot
from src.entity.unit.ai.Task import *


class AdvPilot(Pilot):
    def init(self):
        self.move = Path(self)
        self.hunt = Hunt(self)
        self.hunt.move = self.move
        self.hunt.attack = Melee(self, 1)

    def update(self):
        self.task.update()
        if self.host.delay == 0:
            if not self.dodge():
                self.perceive(self.range)
                if self.task.is_done() and self.task.next:
                    self.task = self.task.next
                    self.task.on_set()
                self.task.perform()

    def add_task(self, task):
        task.next = self.task
        self.task = task
        self.task.on_set()

    def hit(self):
        if self.priority > 1:
            self.priority = 3
            self.add_task(Search(self))

    def prioritize(self, targets):
        nearest_dist = 10
        nearest = targets[0]
        for i in targets:
            t = (i.pos - self.host.pos).distance()
            if t < nearest_dist:
                nearest_dist = t
                nearest = i
        return nearest

    def dodge(self):
        for i in self.host.location.attack.registry:
            if i[2] == self.host.pos:
                self.host.input('block', None)
                return True

    def strategize(self):
        if self.host.weapon.name == 'Bow':
            self.hunt.attack = Range(self)
        else:
            self.hunt.attack = Melee(self, 1)
