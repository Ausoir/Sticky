from src.entity.unit.ai import Tactic


class Behavior:
    def __init__(self, host, fight_type):
        self.host = host
        self.priority = 5
        self.behave = None
        self.tactic = getattr(Tactic, fight_type)(host)
        self.arguments = None

    def set(self, behavior, arg):
        if hasattr(self, behavior):
            self.behave = getattr(self, behavior)
            self.arguments = arg

    def perform(self):
        self.behave()

    def idle(self):
        self.priority = 5

    def hunt(self):
        self.priority = 1
        nearest_dist = 10
        nearest = self.arguments[0]
        for i in self.arguments:
            if not i.is_dead():
                t = (i.pos[0] - self.host.pos[0]).distance()
                if t < nearest_dist:
                    nearest_dist = t
                    nearest = i
        return self.tactic.hunt(nearest)

    def react(self):
        pass
