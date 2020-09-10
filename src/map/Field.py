class Field:
    def __init__(self, location):
        self.location = location
        self.registry = []

    def turn(self):
        count = len(self.registry)
        while count > 0:
            count -= 1
            if self.registry[count][1] == 0:
                self.perform(self.registry[count])
                self.registry.pop(count)
                count -= 1
            elif self.registry[count][1] > 0:
                self.registry[count][1] -= 1
            else:
                self.registry.pop(count)
                count -= 1

    def register(self, damage, pos, delay=0, hitter=None, sound=None, callback=None):
        data = [hitter, delay, pos, damage, sound, callback]
        if delay <= 0:
            self.perform(data)
        else:
            self.registry.append(data)

    def unregister(self, victim):
        for i in self.registry:
            if i[0] == victim:
                i[1] = -1

    def perform(self, data):
        if data[4]:
            self.location.sound.register(data[0].pos, data[4][1], file=data[4][0])
        if data[2] and data[2].things:
            things = data[2].things.copy()
            things.sort(key=lambda _: _.obstruct_type)
            things.reverse()
            for thing in things:
                if thing.hittable:
                    hit = thing.hit(data[3], hitter=data[0])
                    if data[5]:
                        data[5](hit, thing)
                    if hit == -1:
                        return
