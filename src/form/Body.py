from src.form.Appendage import Appendage
from src.other.Data import Data
from src.other.Timer import Timer


class Body:
    def __init__(self, pos, texture_name):
        data = Data.get_cache_clip(texture_name).copy()
        self.pos = pos
        self.model = data[0]
        self.animation = data[1]
        self.motion = {}
        self.organs = []
        self.current_clip = 0
        self.current_motion = []
        self.timer = Timer(0, repeat=1)
        self.direction = 1

        for x in data[2]:
            self.motion[x[0]] = x[1]
        parent = []
        for x in self.model:
            parent.append(x[0])
            self.organs.append(Appendage(self.pos, texture_name=x[1], resize=x[2]))
        for k, x in enumerate(self.organs):
            if abs(parent[k]) != k:
                x.set_parent(self.organs[abs(parent[k])], parent[k] < 0)
        for k, organ in enumerate(self.organs):
            organ.edge.load(organ.pos.x + self.animation[0][k][0], organ.pos.y + self.animation[0][k][1])
        self.set('Idle')

    def update(self):
        if self.timer.update():
            self.current_clip += 1
            self.set_clip()
        else:
            if self.current_clip == -1:
                clip = self.animation[self.current_motion[self.current_clip]]
            else:
                clip = self.animation[self.current_motion[self.current_clip]]
            for k, organ in enumerate(self.organs):
                x = (((clip[k][0] * self.direction) + organ.pos.x) - organ.edge.x) / self.timer.max
                y = ((clip[k][1] + organ.pos.y) - organ.edge.y) / self.timer.max
                organ.edge += (round(x), round(y))
                organ.update()

    def set(self, state):
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

    def face(self, direction):
        self.direction = direction
        for x in self.organs:
            x.form.face(direction)
