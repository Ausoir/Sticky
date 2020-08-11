from pyglet.media import Player

from src.game import Global
from src.game.Camera import Camera
from src.tools.Data import Data


class Sound:
    def __init__(self, location):
        self.location = location
        self.play = Player()
        self.play_bgm = Player()
        self.tab = []
        self.priority = 3
        self.frame = 0
        self.rest = 0
        self.phase = 0
        self.repeat = 0

    def set_bgm(self, tab, rest, repeat=1):
        self.tab = tab
        self.rest = rest
        self.repeat = repeat

    def update_bgm(self):
        if self.repeat > 0:
            self.frame += 1
            if self.frame >= self.rest:
                self.frame = 0
                track = self.tab[self.phase]
                if track:
                    self.play_bgm.queue(Data.get_track(track))
                    if self.play_bgm.playing:
                        self.play_bgm.next_source()
                    else:
                        self.play_bgm.pause()
                    self.play_bgm.play()
                self.phase += 1
                if self.phase >= len(self.tab):
                    self.phase = 0
                    self.repeat -= 1

    def register(self, pos, magnitude, file=None, priority=3):
        if magnitude > 0:
            units = self.location.population.get_units()
            for unit in units:
                if (unit.pos - pos).difference() <= min(magnitude, 13):
                    unit.pilot.hear(pos)
        if file:
            if Camera.target and (pos - Camera.target.pos).difference() < 13:
                self.play.queue(Data.get_track(file))
                if self.play.playing:
                    if priority <= self.priority:
                        self.play.next_source()
                        self.play.play()
                else:
                    self.play.pause()
                    self.play.play()
                self.priority = priority
