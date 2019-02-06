from src.game.Group import Group


class Prompt:
    def __init__(self, callback):
        Group.interface.append(self)
        self.callback = callback

    def input(self, arg):
        if self.callback(arg):
            Group.interface.remove(self)
        return 1
