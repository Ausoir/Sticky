import random

from src.form.Appendage import Appendage
from src.game import Global
from src.tools.Data import Data
from src.tools.Math import Math
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
        self.root = None

        for x in data[2]:
            self.motion[x[0]] = x[1]
        parent = []
        for x in self.model:
            parent.append([x[0], x[1]])
            organ = Appendage(Data.run_cache(x[2]), meta=x[3])
            self.organs.append(organ)
        for k, x in enumerate(self.organs):
            if parent[k][0] == 'r':
                self.root = x
            else:
                int_parent = int(parent[k][1])
                x.set_parent(self.organs[int_parent], parent[k][0])
        self.set('idle')
        for k, organ in enumerate(self.organs):
            # noinspection PyTypeChecker
            x = self.current_animation[k][0] + self.current_animation[len(self.current_animation) - 2][0]
            # noinspection PyTypeChecker
            y = self.current_animation[k][1] + self.current_animation[len(self.current_animation) - 2][1]
            organ.lower_joint.load(x, y)

    def randomize(self, seed):
        self.seed = seed
        self.randomize_body(seed)

    def draw(self, surface, x, y):
        for i in self.organs:
            i.draw(surface, x, y)

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
            self.root.upper_joint.load(self.current_animation[len(self.current_animation) - 2])

    def set(self, state):
        if self.state_name in self.motion:
            self.state_name = state
        else:
            self.state_name = 'idle'
        self.current_clip = 0
        self.update_clip()

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
        self.direction = direction
        for x in self.organs:
            x.form.direction = [self.direction, 0]

    def randomize_once(self, mag):
        r = []
        for k, i in enumerate(self.current_animation):
            if k < len(self.current_animation) - 2:
                r.append([i[0] + Global.r.rand_int(-mag, mag), i[1] + Global.r.rand_int(-mag, mag)])
            else:
                r.append(i)
        self.current_animation = r

    def randomize_clip(self, arg, mag):
        for clip in self.motion[arg]:
            if clip != -1:
                r = []
                for k, i in enumerate(self.animation[clip]):
                    if k < len(self.animation[clip]) - 2:
                        r.append([i[0] + random.randint(-mag, mag), i[1] + random.randint(-mag, mag)])
                    else:
                        r.append(i)
                self.animation[clip] = r

    def randomize_body(self, seed):
        random.seed(seed)
        mag = random.gauss(.6, .1)
        r = []
        for clip in self.animation:
            r1 = []
            for k, i in enumerate(clip):
                if k < len(clip) - 1:
                    r1.append([int(i[0] * mag), int(i[1] * mag)])
                else:
                    r1.append(i)
            r.append(r1)
        self.animation = r

    def rotate_appendage(self, frame, organ, target, offset=0):
        animation = Data.get_cache_clip(self.model_name)[1]
        length = abs(animation[frame][organ][0]) + abs(animation[frame][organ][1])
        atan = target.to_int().get_atan() + (offset * self.direction)
        self.animation[frame][organ][0] = length*Math.cos(atan)*self.direction
        self.animation[frame][organ][1] = length*Math.sin(atan)
