from pyglet.media import Player


class Sound:
    def __init__(self, location):
        self.location = location
        self.play = Player()
        self.priority = 3

    def register(self, pos, magnitude, file=None, priority=3):
        if magnitude > 0:
            units = self.location.population.get_units()
            for unit in units:
                if (unit.pos - pos).difference() <= min(magnitude, 13):
                    unit.pilot.hear(pos)
        if file:
            from src.game.Camera import Camera
            if (pos - Camera.target.pos).difference() < 13:
                from src.tools.Data import Data
                self.play.queue(Data.get_track(file))
                if self.play.playing:
                    if priority <= self.priority:
                        self.play.next_source()
                        self.play.play()
                else:
                    self.play.pause()
                    self.play.play()
                self.priority = priority
