import pygame

from src.game import Global
from src.game.Turn import Turn
from src.interface.Window import Window


class Menu:
    def __init__(self, host):
        Turn.add(self)
        self.host = host
        self.visible = -1
        self.state = self.menu_main
        self.current_state = self.menu_main
        self.window = Window([180, 300], (300, 120))
        self.sub_window = Window(self.window.size.to_list(), (self.window.vec.x + self.window.size.x, 120))
        self.dialog = Window([400, 300], (300, 120))
        self.dialog.color = Window.fore_color1
        self.dialog_text = []
        self.last_input = None
        self.history = []
        self.var = 0

    def draw(self, surface):
        if self.visible == 1:
            self.sub_window.draw(surface)
            self.window.draw(surface)

    def turn(self):
        if self.visible == 1:
            self.state = self.current_state
            self.display(1)
            if self.last_input:
                self.input(self.last_input)

    def input(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.last_input = event
        if self.window.input(event):
            return 1
        if self.sub_window.input(event):
            return 1
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.history.pop()
                if self.history:
                    self.state = self.history[len(self.history) - 1]
                else:
                    self.toggle()
                self.display(1)
            return 1

    def toggle(self):
        self.history = [self.menu_main]
        self.visible *= -1
        self.display(self.visible)

    def display(self, visible):
        self.visible = visible
        self.sub_window.display(-1)
        self.window.display(-1)
        if self.visible == 1:
            self.window.flush()
            self.sub_window.flush()
            self.current_state = self.state
            self.state()
            self.state = self.menu_main
            self.window.display(1)

    def direct(self, page):
        self.history.append(page)
        self.state = page
        self.display(1)

    @staticmethod
    def make_button(text, callback, r_callback, color=Window.fore_color2, width=160, hover=True):
        button = Window([width, 40], color=color)
        button.set_text(text)
        button.on_click = callback
        button.on_r_click = r_callback
        if not hover:
            button.hover_font_color = button.normal_font_color
        return button

    def show_dialog(self, text):
        self.dialog_text = text
        self.direct(self.menu_dialog)

    def menu_dialog(self):
        x = self.window.size.x + self.sub_window.size.x - self.window.margin.x * 2
        textbox = Window([x, 1], color=Window.fore_color2)
        textbox.text_spacing = Global.font.size('A')[1] + 2
        textbox.set_text(self.dialog_text + [' '])
        textbox.hover_font_color = textbox.normal_font_color
        self.window.add_child(textbox)
        self.sub_window.display(1)

    def get_message(self, msg):
        def message():
            self.show_dialog(msg)
        return message

    def menu_main(self):
        self.window.add_child(Menu.make_button(['Main Menu'], None, None))
