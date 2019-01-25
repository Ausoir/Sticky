from src.form.Effect import Effect
from src.game.Turn import Turn


class Attack:
    BATTER = 1
    BLOODY = 2

    def __init__(self):
        Turn.queue.append(self)
        self.registry = []
        self.delay = 0

    def turn(self):
        new_reg = []
        while self.registry:
            new = self.registry.pop(0)
            if new[0] == 0:
                self.hit(new)
            else:
                new[0] -= 1
                new_reg.append(new)
        self.registry = new_reg

    def register(self, inflictor, damage, offset, delay=0, type=BATTER, callback=None):
        tile = inflictor.pos + offset
        self.registry.append([delay, inflictor.location.get_tile(tile), inflictor, damage, type, callback])

    def hit(self, data):
        for thing in data[1].things:
            thing.hit(data[2], data[3])
            if data[4] == Attack.BATTER:
                Effect.batter(data[1].get_center())
            elif data[4] == Attack.BLOODY:
                Effect.blood(data[1].get_center())
            if data[5]:
                data[5](thing)
