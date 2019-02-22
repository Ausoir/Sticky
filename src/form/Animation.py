class Animation:
    def __init__(self, clips, speed, repeat=1):
        self.visible = 1
        self.speed = speed
        self.clips = clips
        self.current = 0
        self.direction = 1
        self.size = clips[0].size
        self.repeat = repeat
        self.ended = 0

    def create(self):
        self.visible = 1
        self.current = 0
        return Animation(self.clips, self.speed, self.repeat)

    def draw(self, surface, x, y):
        if self.visible:
            frame = self.get_current_frame()
            self.clips[frame].face(self.direction)
            self.clips[frame].draw(surface, x, y)

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
        self.direction = direction
