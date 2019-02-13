from src.form.Sprite import Sprite
from src.game.Group import Group
from src.tools.Random import Random


class Effect:
    @classmethod
    def burn(cls, pos, dir=1):
        return cls(['GFX_0x0', 'GFX_0x1', 'GFX_0x2', 'GFX_0x3', 'GFX_0x4'], pos, speed=6, dir=dir)

    @classmethod
    def wind(cls, pos, dir=1):
        return cls(['GFX_1x0', 'GFX_1x1', 'GFX_1x2', 'GFX_1x3', 'GFX_1x4'], pos, speed=6, dir=dir)

    @classmethod
    def explode(cls, pos, dir=1):
        return cls(['GFX_2x0', 'GFX_2x1', 'GFX_2x2', 'GFX_2x3', 'GFX_2x4'], pos, speed=6, dir=dir)

    @classmethod
    def barrier(cls, pos, dir=1):
        return cls(['GFX_3x0', 'GFX_3x1', 'GFX_3x2', 'GFX_3x3', 'GFX_3x4'], pos, speed=6, dir=dir)

    @classmethod
    def kindle(cls, pos, dir=1):
        return cls(['GFX_4x0', 'GFX_4x1', 'GFX_4x2', 'GFX_4x3', 'GFX_4x4'], pos, speed=6, dir=dir)

    @classmethod
    def zip(cls, pos, dir=1):
        return cls(['GFX_5x0', 'GFX_5x1', 'GFX_5x2', 'GFX_5x3', 'GFX_5x4'], pos, speed=6, dir=dir)

    @classmethod
    def batter(cls, pos, dir=1):
        return cls(['GFX_6x0', 'GFX_6x1', 'GFX_6x2', 'GFX_6x3', 'GFX_6x4'], pos, dir=dir)

    @classmethod
    def blood(cls, pos, dir=1):
        return cls(['GFX_7x0', 'GFX_7x1', 'GFX_7x2', 'GFX_7x3', 'GFX_7x4'], pos, dir=dir)

    @classmethod
    def energy(cls, pos, dir=1):
        return cls(['GFX_8x0', 'GFX_8x1', 'GFX_8x2', 'GFX_8x3', 'GFX_8x4'], pos, dir=dir)

    def __init__(self, clips, pos, speed=2, dir=1):
        Group.effects.append(self)
        self.visible = 1
        self.speed = speed
        self.clips = []
        self.current = 0
        self.pos = pos + (Random.rand_int(-16, 16), Random.rand_int(-16, 16))
        for i in clips:
            sprite = Sprite(texture_name=i)
            self.clips.append(sprite)
            sprite.face(dir)

    @staticmethod
    def get(arg):
        return getattr(Effect, arg)

    def draw(self, surface):
        frame = int(self.current/self.speed)
        if frame >= self.clips.__len__():
            self.remove()
        else:
            self.clips[frame].draw(surface, self.pos.x, self.pos.y)
            self.current += 1

    def remove(self):
        Group.effects.remove(self)
