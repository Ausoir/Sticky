from src.game import Global
from src.game.Camera import Camera
from src.tools.Data import Data


class Sound:
    def __init__(self, location):
        self.location = location
        self.tab = []
        self.frame = 0
        self.rest = 0
        self.phase = 0
        self.repeat = 0
        self.play_step = None

    def initialize(self):
        bgm = []
        Global.r_t.reset(Global.player.tags.get('seed'))
        for i in [1, 2, 0, 0, 3, 4, 5, 6, 0, 0, 0]:
            if i != 0:
                bgm.append(Global.r_t.rand_list(['k_[', 'k_1', 'k_3', 'k_o']))
        self.set_bgm(bgm, 3)
        self.play_step = Data.get_track('step')

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
                    Data.get_track(track).play()
                self.phase += 1
                if self.phase >= len(self.tab):
                    self.phase = 0
                    self.repeat -= 1

    def register(self, pos, magnitude, file=None):
        if magnitude > 0:
            units = self.location.population.get_units()
            for unit in units:
                if (unit.pos - pos).difference() <= min(magnitude, 13):
                    unit.pilot.hear(pos)
        if file and Camera.target:
            if pos.is_seen() or (pos - Camera.target.pos).difference() <= min(magnitude + 2, 13):
                if file == 'step':
                    self.play_step.play()
                else:
                    Data.get_track(file).play()
