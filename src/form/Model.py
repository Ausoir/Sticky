from src.form.Picture import Picture


class Model(Picture):
    def __init__(self, clips, **kwargs):
        super().__init__(clips[0], **kwargs)
        self.clips = clips

    def switch(self, index):
        self.set(self.clips[index])
