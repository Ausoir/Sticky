import pygame

from src.game import Global


class Textbox:
    def __init__(self, player, x, y):
        self.player = player
        self.display = 0
        self.display_text = ''
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)
        self.pos = [x, y]

    def input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in Global.player.control.keymap:
                if Global.player.control.keymap[event.key] == 'text':
                    self.display = 100
                    self.color1 = (200, 230, 200)
                    self.color2 = (60, 100, 60)
                    Global.main.text_mode = False
                    Global.player.control.player.input('command', (0, 0))
                    return
            self.display = -1
            self.color1 = (220, 220, 220)
            self.color2 = (40, 40, 40)
            if event.key == pygame.K_BACKSPACE:
                self.display_text = self.display_text[:-1]
            elif event.key == pygame.K_SPACE:
                self.display_text += ' '
            else:
                self.display_text += pygame.key.name(event.key)

    def text(self, arg, time=200):
        self.display = time
        self.display_text = arg
        length = 0
        for char in arg:
            length += Global.font.size(char)[0]
        self.pos[0] = Global.CENTER[0] - int(length/2)

    def draw(self, surface):
        if self.display:
            surface.blit(Global.font.render(self.display_text, 1, self.color2), self.pos)
            surface.blit(Global.font.render(self.display_text, 1, self.color1), (self.pos[0] + 3, self.pos[1] + 1))
            self.display -= 1
