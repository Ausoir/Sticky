import pyglet

from src.game import Global


class Textbox:
    def __init__(self, player, pos):
        self.player = player
        self.display = 0
        self.display_text = ''
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)
        self.pos = pos
        self.word_offset = 0

    def input(self, code):
        if code in Global.player.control.keymap:
            if Global.player.control.keymap[code] == 'text':
                self.display = 100
                self.color1 = (200, 230, 200)
                self.color2 = (60, 100, 60)
                Global.main.text_mode = False
                Global.player.control.player.input('command', (0, 0))
                return
            elif Global.player.control.keymap[code] == 'quit':
                self.display_text = ''
                Global.main.text_mode = False
                return
        self.display = -1
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)
        if code == pyglet.window.key.BACKSPACE:
            self.display_text = self.display_text[:-1]
        elif code == pyglet.window.key.SPACE:
            self.display_text += ' '
        else:
            self.display_text += pyglet.window.key.symbol_string(code)

    def text(self, arg, time=200):
        self.display = time
        self.display_text = arg
        length = 0
        for char in arg:
            length += Global.font.size(char)[0]
        self.word_offset = -int(length/2)

    def draw(self, surface):
        if self.display:
            text1 = Global.font.render(self.display_text, 1, self.color2)
            surface.blit(text1, (self.pos[0] + self.word_offset, self.pos[1]))
            text2 = Global.font.render(self.display_text, 1, self.color1)
            surface.blit(text2, (self.pos[0] + self.word_offset + 3, self.pos[1] + 1))
            self.display -= 1
