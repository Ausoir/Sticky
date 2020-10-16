from pyglet.media import Player

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
        self.players = [[0, Player()], [0, Player()], [0, Player()], [0, Player()], [0, Player()], [0, Player()]]
        self.play_step = Player()
        self.step_track = None

    def initialize(self):
        bgm = []
        Global.r_t.reset(Global.player.tags.get('seed'))
        for i in [1, 2, 0, 0, 3, 4, 5, 6, 0, 0, 0]:
            if i != 0:
                bgm.append(Global.r_t.rand_list(['k_[', 'k_1', 'k_3', 'k_o']))
        self.set_bgm(bgm, 3)
        self.step_track = Data.get_track('step')

    def set_bgm(self, tab, rest, repeat=1):
        self.tab = tab
        self.rest = rest
        self.repeat = repeat

    def turn(self):
        for i in range(len(self.players)):
            if self.players[i][0] > 0:
                self.players[i][0] = self.players[i][0] - 1
                if self.players[i][0] == 0:
                    self.players[i][1].next_source()
        # if self.repeat > 0:
        #     self.frame += 1
        #     if self.frame >= self.rest:
        #         self.frame = 0
        #         track = self.tab[self.phase]
        #         if track:
        #             self.play(track)
        #         self.phase += 1
        #         if self.phase >= len(self.tab):
        #             self.phase = 0
        #             self.repeat -= 1

    def play(self, track):
        for i in self.players:
            if i[0] == 0:
                i[1].queue(Data.get_track(track))
                i[1].play()
                i[0] = 3
                break

    def register(self, pos, magnitude, file=None):
        if magnitude > 0:
            units = self.location.population.get_units()
            for unit in units:
                if (unit.pos - pos).difference() <= min(magnitude, 13):
                    unit.pilot.hear(pos)
        if file and Camera.target:
            if pos.is_seen() or (pos - Camera.target.pos).difference() <= min(magnitude + 2, 13):
                if file == 'step':
                    if self.play_step.playing:
                        self.play_step.pause()
                        self.play_step.seek(0)
                        self.play_step.queue(self.step_track)
                        self.play_step.play()
                    else:
                        self.play_step.play()
                else:
                    self.play(file)

    def exit(self):
        if self.play_step.playing:
            self.play_step.pause()
        for i in self.players:
            if i[1].playing:
                i[1].pause()
