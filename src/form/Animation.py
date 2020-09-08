from src.form.Picture import Picture


class Animation(Picture):
    def __init__(self, clips, delay, loop):
        super().__init__(clips[0])
        self.clips = clips
        self.speed = delay
        self.current = 0
        self.repeat = loop
        self.ended = 0

    def place(self, x, y, **kwargs):
        frame = self.get_current_frame()
        if frame != -1:
            self.set(self.clips[frame])
            super().place(x, y, **kwargs)

    def rotate(self, angle):
        for i in self.clips:
            i.rotation = angle

    def get_current_frame(self):
        r = int(self.current/self.speed)
        if r >= self.clips.__len__():
            self.ended = 1
            if self.repeat == 0:
                self.current = -1
                self.enable(False)
            elif self.repeat == 1:
                self.current = 0
            elif self.repeat == 2:
                self.current = self.clips.__len__() - 1
            r -= 1
        self.current += 1
        return r
