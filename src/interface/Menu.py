from src.game import Global
from src.game.Script import Script
from src.game.Turn import Turn
from src.interface.Window import Window
from src.tools.Data import Data


class Menu:
    def __init__(self, host):
        Turn.add(self.turn)
        self.host = host
        self.visible = -1
        self.state = self.menu_message
        self.current_state = self.menu_message
        width = 180
        self.window = Window(300, 120, width=width, height=300)
        self.window.hover_color = None
        self.sub_window = Window(self.window.x + width, 120, width=width, height=self.window.height)
        self.sub_window.hover_color = None
        self.dialog = Window(300, 120, width=400, height=300)
        self.dialog.color = Window.fore_color1
        self.last_input = None
        self.history = []
        self.history_var = []
        self.var = []

    def turn(self):
        if self.visible == 1:
            self.state = self.current_state
            # self.display(1)
            if not self.window.input(0):
                self.sub_window.input(0)

    def previous(self):
        if self.visible == 1 and len(self.history) > 1:
            self.history.pop()
            self.history_var.pop()
            if self.history:
                self.state = self.history[len(self.history) - 1]
                self.var = self.history_var[len(self.history_var) - 1]
            else:
                self.toggle()
            self.display(1)
        else:
            self.toggle()

    def input(self, event):
        if self.window.input(event):
            return 1
        if self.sub_window.input(event):
            return 1
        if event == 1:
            self.previous()
        elif event == 4:
            self.previous()
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
        self.history = []
        self.history_var = []
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
            self.window.display(1)

    def direct(self, page):
        self.history.append(page)
        self.history_var.append(self.var)
        self.state = page
        self.display(1)

    @staticmethod
    def make(text, callback, name=0, color=Window.fore_color2, width=160, height=40,
             resize=False, hover=True):
        if not color:
            color = Window.fore_color_transparent
        button = Window(0, 0, width=width, height=height, name=name, color=color, multi_line=resize)
        button.set_text(text)
        button.on_click = callback
        if not hover:
            button.hover_color = None
        return button

    def menu_message(self):
        x = self.window.width + self.sub_window.width - self.window.margin.x * 2
        height = 300 - (self.window.margin.y * 2)
        textbox = Window(0, 0, width=x, height=height, color=Window.fore_color2, multi_line=True)
        textbox.text_spacing = Global.font.ascent - Global.font.descent + 2
        textbox.set_text(self.var[0])
        textbox.update_text()
        textbox.hover_color = None
        self.window.add(textbox)
        self.sub_window.display(1)

    def get_message(self, msg):
        def message(index):
            self.var = [msg]
            self.direct(self.menu_message)
        return message

    def get_prompt(self, msg, choice, cb, param=0):
        def message(index):
            self.var = [msg, choice, cb, param]
            self.direct(self.menu_prompt)
        return message

    @staticmethod
    def get_conversation(dialogs):
        output = []
        for sentence in dialogs:
            new = ','.join(sentence)
            output.append(new)
        return output

    def menu_prompt(self):
        text = self.var[0]
        self.window.add(Menu.make(text, None, color=Window.fore_color_transparent,
                                  hover=False, width=320, resize=True))
        self.window.next_y = self.window.height + self.window.y
        button = Menu.make(self.var[1], self.var[2], name=self.var[3], width=320)
        self.window.add(button, reverse=True, index=0)
        self.sub_window.display(1)

    def menu_choice(self):
        if self.var[0]:
            text = self.var[0]
            self.window.add(Menu.make(text, None, color=Window.fore_color_transparent,
                                      hover=False, width=320, resize=True))
            self.window.next_y = self.window.height + self.window.y
            for i in self.var[1]:
                button = Menu.make(i[0], Script.execute_code, name=i[1], width=320)
                self.window.add(button, reverse=True, index=0)
        else:
            for i in self.var[1]:
                button = Menu.make(i[0], Script.execute_code, name=i[1], width=320)
                self.window.add(button)
        self.sub_window.display(1)

    def menu_many_choice(self):
        wide = False
        for k, v in enumerate(self.var):
            length = len(self.var[k])
            if length == 0:
                button = Menu.make('', None, color=None)
            elif length > 1:
                button = Menu.make(self.var[k][0], Script.execute_code, name=self.var[k][1])
            else:
                button = Menu.make(self.var[k][0], None, color=None)
            if k < 6:
                self.window.add(button)
            else:
                wide = True
                self.sub_window.add(button)
        if wide:
            self.sub_window.display(1)

    def menu_conversation(self):
        self.window.add(Menu.make(self.var[0], None, color=None, hover=False, resize=True))
        for option in self.var[1:]:
            self.sub_window.add(Menu.make(option[0], Script.execute_code, width=160, name=option[1]))
        self.sub_window.display(1)

    def topic(self, name):
        topic = Data.get_line('raw/menu.txt', name.lower())
        if topic:
            self.var = topic[2]
            if topic[1] == 1:
                self.get_message(topic[2][0])(None)
            elif topic[1] == 2:
                def confirm(index):
                    Script.execute_code(topic[2][2])
                self.get_prompt(topic[2][0], topic[2][1], confirm)(None)
            elif topic[1] == 3:
                self.direct(self.menu_conversation)
            elif topic[1] == 4:
                self.direct(self.menu_choice)
            elif topic[1] == 5:
                self.direct(self.menu_many_choice)
