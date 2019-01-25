from src.form.Appendage import Appendage
from src.tools.Data import Data
from src.tools.Random import Random
from src.tools.Timer import Timer


class Body:
    def __init__(self, texture_name, seed):
        data = Data.get_cache_clip(texture_name).copy()
        self.model = data[0]
        self.animation = data[1]
        self.randomize_body(seed)
        self.motion = {}
        self.organs = []
        self.current_clip = 0
        self.current_motion = []
        self.timer = Timer(0, repeat=1)
        self.direction = 1
        self.current_animation = None
        self.offset_x = 0
        self.state_name = 'idle'

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
            i.draw(surface, x + self.offset_x, y)

    def update(self):
        if self.timer.update():
            self.current_clip += 1
            self.set_clip()
        else:
            for k, organ in enumerate(self.organs):
                x = (((self.current_animation[k][0] * self.direction) + organ.offset.x) - organ.edge.x) / self.timer.max
                y = ((self.current_animation[k][1] + organ.offset.y) - organ.edge.y) / self.timer.max
                organ.edge += (x, y)
                organ.update()

    def set(self, state):
        self.state_name = state
        self.current_motion = self.motion[state]
        self.current_clip = 0
        self.set_clip()

    def set_clip(self):
        if self.current_clip >= self.current_motion.__len__():
            self.current_clip = 0
        if self.current_motion[self.current_clip] == -1:
            self.current_clip -= 1
        clip = self.animation[self.current_clip]
        frame = clip[clip.__len__()-1]
        self.timer.set(frame)
        self.current_animation = self.animation[self.current_motion[self.current_clip]]

    def set_speed(self, turn):
        speed = min(turn+1, self.timer.max)
        self.timer.set(max(1, speed))

    def face(self, direction):
        self.direction = direction
        for x in self.organs:
            x.face(direction)

    def set_height(self, arg=0):
        height = arg
        if not arg:
            for i in self.organs:
                if i.leg:
                    height = i.edge.y - 4
                    break
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
        self.offset_x = random.randint(-2, 2)
        mag = random.gauss(1, .1)
        r = []
        for clip in self.animation:
            r1 = []
            for i in clip:
                if isinstance(i, list):
                    r1.append([i[0], i[1] * mag])
                else:
                    r1.append(i)
            r.append(r1)
        self.animation = r
