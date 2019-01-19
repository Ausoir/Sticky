from src.interface.Window import Window


class Menu:
    def __init__(self):
        self.visible = -1
        self.state = self.menu_main
        self.window = Window(1, [160, 300], (300, 120))
        self.sub_window = Window(1, self.window.size, (self.window.vec.x + self.window.size[0], 120))
        self.dialog = Window(1, [400, 300], (300, 120))
        self.dialog.color = Window.fore_color1
        self.dialog_text = []

    def toggle(self):
        self.visible *= -1
        self.display(self.visible)

    def display(self, visible):
        self.visible = visible
        self.sub_window.display(-1)
        self.window.display(-1)
        if self.visible == 1:
            self.window.flush()
            self.sub_window.flush()
            self.state()
            self.state = self.menu_main
            self.window.display(1)

    @staticmethod
    def make_button(text, callback):
        button = Window(2, [140, 40], color=Window.fore_color2)
        button.set_text(text)
        button.on_click = callback
        return button

    def show_dialog(self, text):
        self.dialog_text = text
        self.state = self.menu_dialog
        self.display(1)
        self.window.visible = -1

    def menu_dialog(self):
        textbox = Window(3, [400, 300], color=Window.fore_color2)
        textbox.set_text(self.dialog_text)
        textbox.on_click = self.toggle
        textbox.spacing = 28
        self.window.add_child(textbox)

    def menu_main(self):
        self.window.add_child(Menu.make_button(['Skills'], self.click_skills))
        self.window.add_child(Menu.make_button(['Character'], self.click_character))
        self.window.add_child(Menu.make_button(['Equipment'], self.click_equipment))

    def menu_character(self):
        def describe():
            self.show_dialog(['Something HP', 'Some long dialog text.....', 'And your choice'])
        text = ['HP - 3/3', 'Str - 1', 'Agi - 1', 'Int - 1', 'Nutrition - 5/5']
        panel = Menu.make_button(text, describe)
        panel.color = Window.fore_color3
        panel.depth = 2
        panel.redraw()
        self.window.add_child(panel)
        self.sub_window.add_child(Menu.make_button(['Mastery'], self.click_mastery))
        self.sub_window.add_child(Menu.make_button(['Status'], self.click_status))
        self.sub_window.display(1)

    def menu_skills(self):
        text = ['Airstrike - lvl 1', 'Windwalk - lvl 4']
        panel = Menu.make_button(text, None)
        panel.color = Window.fore_color3
        panel.depth = 2
        panel.redraw()
        self.window.add_child(panel)
        self.sub_window.add_child(Menu.make_button(['Action [1]'], None))
        self.sub_window.add_child(Menu.make_button(['Action [2]'], None))
        self.sub_window.add_child(Menu.make_button(['Action [3]'], None))
        self.sub_window.add_child(Menu.make_button(['Action [Q]'], None))
        self.sub_window.add_child(Menu.make_button(['Action [E]'], None))
        self.sub_window.display(1)

    def menu_equipment(self):
        self.window.add_child(Menu.make_button(['Hat'], None))
        self.window.add_child(Menu.make_button(['Comfort Wear'], None))
        self.window.add_child(Menu.make_button(['Aa Amulet'], None))
        inv = [[1, 0, 1], [1, 0, 1], [0, 1, 0], [1, 0, 1]]
        for ky, vy in enumerate(inv):
            for kx, vx in enumerate(vy):
                color = Window.fore_color3 if vx == 1 else (120, 120, 120, 220)
                slot = Window(2, [40, 40], color=color)
                slot.vec.x = kx * 48
                slot.vec.y = ky * 48
                self.sub_window.add_child(slot)
                self.sub_window.next_y -= slot.size[1] + self.sub_window.margin.y
        textbox = Window(3, [0, 0], color=Window.font_color1)
        textbox.set_text(['Gold: 464'])
        self.window.add_child(textbox)
        self.sub_window.display(1)

    def menu_mastery(self):
        self.window.add_child(Menu.make_button(['Mastery'], None))

    def menu_status(self):
        self.window.add_child(Menu.make_button(['Status'], None))

    def click_character(self):
        self.state = self.menu_character
        self.display(1)

    def click_skills(self):
        self.state = self.menu_skills
        self.display(1)

    def click_equipment(self):
        self.state = self.menu_equipment
        self.display(1)

    def click_mastery(self):
        self.state = self.menu_mastery
        self.display(1)

    def click_status(self):
        self.state = self.menu_status
        self.display(1)
