from src.form.Picture import Picture


class Animation(Picture):
    def __init__(self, clips, speed, loop):
        super().__init__(clips[0])
        self.clips = clips
        self.speed = speed
        self.delay = 0
        self.current = 0
        self.repeat = loop

    def place(self, x, y, **kwargs):
        frame = self.get_current_frame()
        if frame != -1:
            self.set(self.clips[frame])
            super().place(x, y, **kwargs)

    def rotate(self, angle):
        for i in self.clips:
            i.rotation = angle

    def get_current_frame(self):
        self.delay += 1
        if self.delay >= self.speed:
            self.current += 1
            self.delay = 0
        if self.current >= self.clips.__len__():
            if self.repeat == 0:
                self.current = -1
                self.show(False)
                del self
                return -1
            elif self.repeat == 1:
                self.current = 0
            elif self.repeat == 2:
                self.current = self.clips.__len__() - 1
        return self.current
