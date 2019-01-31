from src.entity.Space import Space
from src.form.Appendage import Appendage
from src.tools.Data import Data
from src.tools.Math import Math
from src.tools.Random import Random
from src.tools.Timer import Timer


class Body:
    def __init__(self, texture_name, seed):
        data = Data.get_cache_clip(texture_name).copy()
        self.texture_name = texture_name
        self.model = data[0]
        self.animation = data[1]
        self.randomize_body(seed)
        self.motion = {}
        self.organs = []
        self.current_clip = 0
        self.timer = Timer(0, repeat=1)
        self.direction = 1
        self.current_animation = None
        self.state_name = 'idle'
        self.animation_ended = 0

        for x in data[2]:
            self.motion[x[0]] = x[1]
        parent = []
        for x in self.model:
            parent.append(x[0])
            self.organs.append(Appendage(texture_name=x[1], resize=x[2], organ=x[3]))
        for k, x in enumerate(self.organs):
            if abs(parent[k]) != k:
                x.set_parent(self.organs[abs(parent[k])], parent[k] < 0)
        for k, organ in enumerate(self.organs):
            organ.edge.load(self.animation[0][k][0], self.animation[0][k][1])
        self.set('idle')
        self.set_height()

    def draw(self, surface, x, y):
        for i in self.organs:
            i.draw(surface, x, y)

    def update(self):
        if self.timer.update():
            self.update_clip()
        else:
            for k, organ in enumerate(self.organs):
                x = (((self.current_animation[k][0] * self.direction) + organ.offset.x) - organ.edge.x) / self.timer.max
                y = ((self.current_animation[k][1] + organ.offset.y) - organ.edge.y) / self.timer.max
                organ.edge += (x, y)
                organ.update()

    def set(self, state):
        self.state_name = state
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
            x.face(direction)

    def set_height(self, arg=0):
        if arg:
            height = arg
        else:
            leg_index = 0
            for k, i in enumerate(self.organs):
                if i.leg:
                    leg_index = k
                    break
            height = self.animation[0][leg_index][1] - 4
        for i in self.organs:
            i.height = height

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
            r = []
            for i in self.animation[clip]:
                if isinstance(i, list):
                    r.append([i[0] + Random.rand_int(-mag, mag), i[1] + Random.rand_int(-mag, mag)])
                else:
                    r.append(i)
            self.animation[clip] = r

    def randomize_body(self, seed):
        import random
        random.seed(seed)
        mag = random.gauss(1, .1)
        r = []
        for clip in self.animation:
            r1 = []
            for i in clip:
                if isinstance(i, list):
                    r1.append([i[0], int(i[1] * mag)])
                else:
                    r1.append(i)
            r.append(r1)
        self.animation = r

    def rotate_appendage(self, frame, organ, target):
        animation = Data.get_cache_clip(self.texture_name)[1]
        length = abs(animation[frame][organ][0]) + abs(animation[frame][organ][1])
        atan = Space(target).to_int().get_atan()
        self.animation[frame][organ][0] = length*Math.cos(atan)*-self.direction
        self.animation[frame][organ][1] = length*Math.sin(atan)
