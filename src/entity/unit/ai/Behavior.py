from src.entity.unit.ai import Tactic


class Behavior:
    def __init__(self, host, fight_type):
        self.host = host
        self.priority = 5
        self.behave = None
        self.tactic = getattr(Tactic, fight_type)(host)
        self.arguments = None

    def set(self, *arg):
        if hasattr(self, arg[0]):
            self.behave = getattr(self, arg[0])
            self.arguments = arg[1:]

    def perform(self):
        self.behave()

    def idle(self):
        self.priority = 5

    def hunt(self):
        self.priority = 1
        self.tactic.hunt(self.arguments[0])

    def react(self):
        pass
