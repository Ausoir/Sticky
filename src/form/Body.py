import random

from src.form.Appendage import Appendage, Limb
from src.game import Global
from src.tools.Data import Data
from src.tools.Timer import Timer


class Body:
    TEXTURE_DIRECTION = [0, 1, 2, 1]

    def __init__(self, model_name):
        super().__init__()
        data = Data.get_cache_clip(model_name).copy()
        self.model_name = model_name
        self.texture_count = 0
        self.seed = 1
        self.side = 1
        self.direction = 0
        self.row = 0
        self.model = data[0][0]
        self.order = data[0][1]
        self.animation = data[1]
        self.motion = {}
        self.organs = []
        self.current_clip = 0
        self.timer = Timer(0, repeat=1)
        self.current_animation = None
        self.state_name = 'default'
        self.animation_ended = 0
        self.root = None

        for x in data[2]:
            self.motion[x[0]] = x[1]
        parent = []
        for x in self.model:
            parent.append([x[0], x[1]])
            if len(x) == 2:
                organ = Limb()
            else:
                self.texture_count = max(self.texture_count, x[2] + 1)
                organ = Appendage(x[2], x[3], x[4], x[5])
            self.organs.append(organ)
        for k, x in enumerate(self.organs):
            if parent[k][0] == 'r':
                self.root = x
            else:
                int_parent = int(parent[k][1])
                x.set_parent(self.organs[int_parent], parent[k][0])
        self.force_set_animation('default')

    def show(self, visible):
        for i in self.organs:
            i.form.show(visible)

    def bound(self, visible):
        for i in self.organs:
            i.form.bound(visible)

    def set_model(self, image):
        for i in self.organs:
            if i.texture_num >= 0:
                img = Data.get_form(image, form='Unit' + str(self.texture_count))
                img.show(True)
                i.set(img)
        self.update_perspective()

    def set_row(self, row):
        self.row = row
        t = row
        for i in self.order[self.direction - 1]:
            if i >= 0:
                self.organs[i].form.z = t
                t += 1

    def delete(self):
        for i in self.organs:
            i.form.delete()

    def place(self, x, y):
        if self.timer.update():
            self.update_clip()
        timer = self.timer.time + 1
        root = self.current_animation[len(self.current_animation) - 2]
        dx = (root[0] - self.root.upper_joint.x) / timer
        dy = (root[1] - self.root.upper_joint.y) / timer
        self.root.upper_joint += (dx, dy)
        for k, organ in enumerate(self.organs):
            diff = organ.upper_joint - organ.lower_joint
            dx = ((self.current_animation[k][0] * self.side) + diff.x) / timer
            dy = (self.current_animation[k][1] + diff.y) / timer
            organ.lower_joint += (dx, dy)
            organ.place(x, y)

    def force_set_animation(self, motion):
        self.current_animation = self.animation[self.motion[motion][0]]
        for k in self.order[self.direction]:
            if k >= 0:
                organ = self.organs[k]
                x = self.current_animation[k][0]
                x *= self.side
                y = self.current_animation[k][1]
                organ.lower_joint.load(organ.upper_joint.x + x, organ.upper_joint.y + y)

    def set_state(self, state):
        if state in self.motion:
            self.state_name = state
        else:
            self.state_name = 'idle'
        self.current_clip = 0
        self.update_clip()

    def update_clip(self):
        self.animation_ended = 0
        current_motion = self.motion[self.get_directional_state()]
        if self.current_clip >= current_motion.__len__():
            self.current_clip = 0
        if current_motion[self.current_clip] == -1:
            self.current_clip -= 1
            self.animation_ended = 1
        self.current_animation = self.animation[current_motion[self.current_clip]]
        frame = self.current_animation[self.current_animation.__len__() - 1]
        self.timer.set(frame)
        self.current_clip += 1

    def get_total_motion_time(self):
        total = 0
        for i in self.motion[self.get_directional_state()]:
            current = self.animation[i]
            total += current[len(current) - 1]
        return total

    def get_directional_state(self, state=None):
        if not state:
            state = self.state_name
        if self.direction == 2 and state + 'U' in self.motion:
            return state + 'U'
        elif self.direction == 0 and state + 'D' in self.motion:
            return state + 'D'
        return state

    def face(self, direction):
        self.direction = direction
        if self.direction in [1, 2]:
            self.face_side(-1)
        else:
            self.face_side(1)
        self.update_perspective()

    def face_side(self, side):
        self.side = side

    def update_perspective(self):
        numeral = Body.TEXTURE_DIRECTION[self.direction] * self.texture_count
        t = self.row
        for i in self.order[self.direction]:
            if i >= 0:
                t += 1
                organ = self.organs[i]
                if organ.texture_num == -1:
                    organ.form.switch(Body.TEXTURE_DIRECTION[self.direction])
                else:
                    organ.form.switch(organ.texture_num + numeral)
                organ.form.reset()
                organ.set(organ.form)
                organ.flip(self.side, self.direction)
                organ.form.z = t

    def randomize(self, seed):
        self.seed = seed
        random.seed(seed)
        mag = random.gauss(.8, .1)
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
