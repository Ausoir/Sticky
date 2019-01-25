from src.form.Sprite import Sprite
from src.game.Group import Group


class Effect:
    @classmethod
    def batter(cls, pos):
        cls(['Hit_0x0', 'Hit_1x0', 'Hit_2x0', 'Hit_3x0'], pos)

    @classmethod
    def blood(cls, pos):
        cls(['Blood_0x0', 'Blood_1x0', 'Blood_2x0', 'Blood_3x0'], pos)

    def __init__(self, clips, pos, speed=2):
        Group.effects.append(self)
        self.visible = 1
        self.speed = speed
        self.clips = []
        self.current = 0
        self.pos = pos
        for i in clips:
            self.clips.append(Sprite(texture_name=i))

    def draw(self, surface):
        frame = int(self.current/self.speed)
        if frame >= self.clips.__len__():
            self.remove()
        else:
            self.clips[frame].draw(surface, self.pos[0], self.pos[1])
            self.current += 1

    def remove(self):
        Group.effects.remove(self)
