from src.entity.Space import Space
from src.form.Form import Form


class Animation(Form):
    def __init__(self, args):
        super().__init__()
        self.clips = args[0]
        self.speed = args[1]
        self.current = 0
        self.repeat = args[2]
        self.ended = 0
        self.size = self.clips[0].size
        self.pivot = Space(self.size.x / 2, self.size.y / 2)

    def draw(self, surface, x, y):
        if self.visible:
            frame = self.get_current_frame()
            self.clips[frame].draw(surface, x, y)

    def rotate(self, angle):
        self.rotation = angle
        for i in self.clips:
            i.rotate(angle)

    def get_current_frame(self):
        r = int(self.current/self.speed)
        if r >= self.clips.__len__():
            self.ended = 1
            if self.repeat == 0:
                self.current = 0
                self.visible = 0
            elif self.repeat == 1:
                self.current = 0
            elif self.repeat == 2:
                self.current = self.clips.__len__() - 1
            r -= 1
        self.current += 1
        return r

    def face(self, direction):
        if self.direction != direction:
            self.direction = direction
            self.rotate(self.rotation + 180)
