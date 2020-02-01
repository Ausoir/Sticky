import pyglet

from src.game.Turn import Turn


class Sound:
    def __init__(self, location):
        Turn.add(self.turn)
        self.play = pyglet.media.Player()
        self.location = location
        self.registry = []

    def turn(self):
        for i in self.registry:
            if i[1] > 0:
                self.update(i)
        self.registry.clear()

    def register(self, pos, magnitude, file=None):
        data = [pos, magnitude]
        self.registry.append(data)
        if file:
            from src.tools.Data import Data
            self.play.queue(Data.get_track(file))
            if self.play.playing:
                self.play.next_source()
            else:
                self.play.pause()
            self.play.play()

    def update(self, data):
        tiles = []
        magnitude = min(data[1], 13)
        for x in range(-magnitude, magnitude + 1):
            tiles.append(data[0] + (x, -magnitude))
            tiles.append(data[0] + (x, magnitude))
        for y in range(-magnitude + 1, magnitude):
            tiles.append(data[0] + (-magnitude, y))
            tiles.append(data[0] + (magnitude, y))
        from src.entity.unit.Unit import Unit
        for i in tiles:
            tile = self.location.get_tile(i)
            for thing in tile.things:
                if isinstance(thing, Unit) and not thing.tags.get('deaf'):
                    thing.pilot.hear(data[0])
