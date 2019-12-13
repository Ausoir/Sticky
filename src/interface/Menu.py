from src.game import Global
from src.game.Turn import Turn
from src.interface.Window import Window


class Menu:
    def __init__(self, host):
        Turn.add(self.turn)
        self.host = host
        self.visible = -1
        self.state = self.menu_main
        self.current_state = self.menu_main
        width = 180
        self.window = Window(300, 120, width=width, height=300)
        self.window.hover_color = None
        self.sub_window = Window(self.window.x + width, 120, width=width, height=self.window.height)
        self.sub_window.hover_color = None
        self.dialog = Window(300, 120, width=400, height=300)
        self.dialog.color = Window.fore_color1
        self.dialog_text = []
        self.last_input = None
        self.history = []
        self.history_var = []
        self.var = []

    def draw(self):
        if self.visible == 1:
            self.sub_window.draw()
            self.window.draw()

    def turn(self):
        if self.visible == 1:
            self.state = self.current_state
            self.display(1)
            if not self.window.input(0):
                self.sub_window.input(0)

    def input(self, event):
        if self.window.input(event):
            return 1
        if self.sub_window.input(event):
            return 1
        if event == 1:
            return 1
        elif event == 4:
            self.history.pop()
            self.history_var.pop()
            if self.history:
                self.state = self.history[len(self.history) - 1]
                self.var = self.history_var[len(self.history_var) - 1]
            else:
                self.toggle()
            self.display(1)
        elif 0x031 <= event <= 0x039:
            index = event - 0x031
            total = self.window.children + self.sub_window.children
            if len(total) > index:
                for i in total:
                    if i.on_click:
                        if index == 0:
                            i.on_click(i.name)
                        index -= 1
            return 1

    def toggle(self):
        self.history = [self.menu_main]
        self.history_var = [0]
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
        self.history_var.append(self.var)
        self.state = page
        self.display(1)

    @staticmethod
    def make(text, callback, r_callback, name=0, color=Window.fore_color2, width=160, resize=False, hover=True):
        if not color:
            color = Window.fore_color_transparent
        button = Window(0, 0, width=width, height=40, name=name, color=color, multi_line=resize)
        button.set_text(text)
        button.on_click = callback
        button.on_r_click = r_callback
        if not hover:
            button.hover_color = None
        return button

    def show_dialog(self, text):
        self.dialog_text = text
        self.direct(self.menu_dialog)

    def menu_dialog(self):
        x = self.window.width + self.sub_window.width - self.window.margin.x * 2
        textbox = Window(0, 0, width=x, height=1, color=Window.fore_color2)
        textbox.text_spacing = Global.font.ascent - Global.font.descent + 2
        textbox.set_text(self.dialog_text)
        textbox.hover_color = None
        self.window.add(textbox)
        self.sub_window.display(1)

    def get_message(self, msg):
        def message(index):
            self.show_dialog(msg)
        return message

    def menu_main(self):
        self.window.add(Menu.make('Main Menu', None, None))

    @staticmethod
    def get_conversation(dialogs):
        output = []
        for sentence in dialogs:
            new = ','.join(sentence)
            output.append(new)
        return output

    def menu_choice(self):
        if self.var[0]:
            text = self.var[0]
            self.window.add(Menu.make(text, None, None, color=Window.fore_color_transparent,
                                      hover=False, width=320, resize=True))
            self.window.next_y = self.window.height + self.window.y
            for i in range(len(self.var[1])):
                button = Menu.make(self.var[1][i], self.var[2][i], None, name=i, width=320)
                self.window.add(button, reverse=True, index=0)
        else:
            for i in range(len(self.var[1])):
                button = Menu.make(self.var[1][i], self.var[2][i], None, name=i, width=320)
                self.window.add(button)
        self.sub_window.display(1)

    def menu_many_choice(self):
        for k, v in enumerate(self.var):
            button = Menu.make(self.var[k][0], self.var[k][1], self.var[k][1], name=self.var[k][0])
            if k < 6:
                self.window.add(button)
            else:
                self.sub_window.add(button)
        self.sub_window.display(1)
