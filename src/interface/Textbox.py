import pygame

from src.game import Global


class Textbox:
    def __init__(self, player):
        self.player = player
        self.display = 0
        self.display_text = ''
        self.color1 = (220, 220, 220)
        self.color2 = (40, 40, 40)

    def input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in Global.main.player.control.keymap:
                if Global.main.player.control.keymap[event.key] == 'text':
                    self.display = 100
                    self.color1 = (220, 250, 220)
                    self.color2 = (40, 100, 40)
                    Global.main.text_mode = False
                    return
            self.display = -1
            self.color1 = (220, 220, 220)
            self.color2 = (40, 40, 40)
            if event.key == pygame.K_BACKSPACE:
                self.display_text = self.display_text[:-1]
            else:
                self.display_text += pygame.key.name(event.key)

    def draw(self, surface):
        if self.display:
            surface.blit(Global.font.render(self.display_text, 1, self.color2), (16, Global.DISPLAY[1] - 48))
            surface.blit(Global.font.render(self.display_text, 1, self.color1), (17, Global.DISPLAY[1] - 47))
            self.display -= 1
