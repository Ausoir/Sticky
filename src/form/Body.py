import random

from src.form.Appendage import Appendage
from src.game import Global
from src.tools.Data import Data
from src.tools.Math import Math
from src.tools.Random import Random
from src.tools.Timer import Timer


class Body:
    LEG = 2

    def __init__(self, model_name):
        data = Data.get_cache_clip(model_name).copy()
        self.seed = 1
        self.model_name = model_name
        self.model = data[0]
        self.animation = data[1]
        self.motion = {}
        self.organs = []
        self.current_clip = 0
        self.timer = Timer(0, repeat=1)
        self.direction = 1
        self.current_animation = None
        self.state_name = 'idle'
        self.animation_ended = 0
        self.height = 0
        self.leg = []

        for x in data[2]:
            self.motion[x[0]] = x[1]
        parent = []
        for x in self.model:
            parent.append(x[0])
            organ = Appendage(Data.run_cache(x[1]), part=x[2], resize=x[3])
            self.organs.append(organ)
        for k, x in enumerate(self.organs):
            if x.part == Body.LEG:
                self.leg.append(k)
            if abs(parent[k]) != k:
                x.set_parent(self.organs[abs(parent[k])], parent[k] < 0)
        for k, organ in enumerate(self.organs):
            organ.lower_joint.load(self.animation[0][k][0], self.animation[0][k][1])
        self.set('idle')

    def randomize(self, seed):
        self.seed = seed
        self.randomize_body(seed)

    def draw(self, surface, x, y):
        for i in self.organs:
            i.draw(surface, x, y - self.height)

    def update(self):
        if self.timer.update():
            self.update_clip()
        else:
            for k, organ in enumerate(self.organs):
                diff = organ.upper_joint - organ.lower_joint
                dx = ((self.current_animation[k][0] * self.direction) + diff.x) / self.timer.max
                dy = (self.current_animation[k][1] + diff.y) / self.timer.max
                organ.lower_joint += (dx, dy)
                organ.update()

    def set(self, state):
        self.state_name = state
        self.current_clip = 0
        self.update_clip()
        self.height = -200
        for i in self.leg:
            self.height = max(self.height, self.current_animation[i][1] - Global.HALF_BLOCK - 1)

    def update_clip(self):
        self.animation_ended = 0
        current_motion = self.motion[self.state_name]
        if self.current_clip >= current_motion.__len__():
            self.current_clip = 0
        if current_motion[self.current_clip] == -1:
            self.current_clip -= 1
            self.animation_ended = 1
        self.current_animation = self.animation[current_motion[self.current_clip]]
        frame = self.current_animation[self.current_animation.__len__()-1]
        self.timer.set(frame)
        self.current_clip += 1

    def face(self, direction):
        if self.direction != direction:
            self.direction = direction
            for x in self.organs:
                x.form.flip(1, 0)

    def randomize_once(self, mag):
        r = []
        for i in self.current_animation:
            if isinstance(i, list):
                r.append([i[0] + Random.rand_int(-mag, mag), i[1] + Random.rand_int(-mag, mag)])
            else:
                r.append(i)
        self.current_animation = r

    def randomize_clip(self, arg, mag):
        for clip in self.motion[arg]:
            if clip != -1:
                r = []
                for i in self.animation[clip]:
                    if isinstance(i, list):
                        r.append([i[0] + random.randint(-mag, mag), i[1] + random.randint(-mag, mag)])
                    else:
                        r.append(i)
                self.animation[clip] = r

    def randomize_body(self, seed):
        random.seed(seed)
        mag = random.gauss(.9, .08)
        r = []
        for clip in self.animation:
            r1 = []
            for i in clip:
                if isinstance(i, list):
                    r1.append([int(i[0] * mag), int(i[1] * mag)])
                else:
                    r1.append(i)
            r.append(r1)
        self.animation = r

    def rotate_appendage(self, frame, organ, target):
        animation = Data.get_cache_clip(self.model_name)[1]
        length = abs(animation[frame][organ][0]) + abs(animation[frame][organ][1])
        atan = target.to_int().get_atan()
        self.animation[frame][organ][0] = length*Math.cos(atan)*self.direction
        self.animation[frame][organ][1] = length*Math.sin(atan)
