from src.game.Turn import Turn


class Turnee:
    def __init__(self, fn, lifetime):
        self.fn = fn
        self.lifetime = lifetime
        Turn.add(self.turn)

    def turn(self):
        if self.lifetime > 0:
            self.lifetime -= 1
            self.fn()
        elif self.lifetime == 0:
            self.fn()
            Turn.remove(self.turn)
