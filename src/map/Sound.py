from pyglet.media import Player


class Sound:
    def __init__(self, location):
        self.location = location
        self.play = Player()
        self.registry = []

    def turn(self):
        for i in self.registry:
            self.update(i)
        self.registry.clear()

    def register(self, pos, magnitude, file=None):
        if magnitude > 0:
            data = [pos, min(magnitude, 13)]
            self.registry.append(data)
        if file:
            from src.game.Camera import Camera
            if (pos - Camera.target.pos).difference() < 13:
                from src.tools.Data import Data
                self.play.queue(Data.get_track(file))
                if self.play.playing:
                    self.play.next_source()
                else:
                    self.play.pause()
                self.play.play()

    def update(self, data):
        units = self.location.population.get_units()
        for unit in units:
            if (unit.pos - data[0]).difference() <= data[1]:
                unit.pilot.hear(data[0])
