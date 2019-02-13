import pygame

from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Turn import Turn
from src.interface.CanvasWindow import CanvasWindow
from src.interface.Window import Window


class Menu:
    def __init__(self, host):
        Turn.add(self)
        self.delay = 1
        self.host = host
        self.visible = -1
        self.state = self.menu_main
        self.current_state = self.menu_main
        self.window = Window([160, 300], (300, 120))
        self.sub_window = Window(self.window.size.to_list(), (self.window.vec.x + self.window.size.x, 120))
        self.dialog = Window([400, 300], (300, 120))
        self.dialog.color = Window.fore_color1
        self.dialog_text = []
        self.changed = 0

    def draw(self, surface):
        if self.visible == 1:
            self.window.draw(surface)
            self.sub_window.draw(surface)

    def turn(self):
        if self.changed and self.visible == 1:
            self.state = self.current_state
            self.display(1)

    def input(self, event):
        if event.type != pygame.MOUSEMOTION\
                and event.type != pygame.MOUSEBUTTONUP and event.type != pygame.MOUSEBUTTONDOWN:
            self.changed = 1
        if self.window.input(event):
            return 1
        if self.sub_window.input(event):
            return 1
        return 0

    def toggle(self):
        self.visible *= -1
        self.display(self.visible)

    def display(self, visible):
        self.visible = visible
        self.sub_window.display(-1)
        self.window.display(-1)
        if self.visible == 1:
            self.changed = 0
            self.window.flush()
            self.sub_window.flush()
            self.current_state = self.state
            self.state()
            self.state = self.menu_main
            self.window.display(1)

    @staticmethod
    def make_button(text, callback, r_callback, color=Window.fore_color2):
        button = Window([140, 40], color=color)
        button.set_text(text)
        button.on_click = callback
        button.on_r_click = r_callback
        return button

    def show_dialog(self, text):
        self.dialog_text = text
        self.state = self.menu_dialog
        self.display(1)
        self.window.visible = -1

    def menu_dialog(self):
        textbox = Window([400, 300], color=Window.fore_color2)
        textbox.set_text(self.dialog_text)
        textbox.on_click = self.toggle
        textbox.text_spacing = 28
        self.window.add_child(textbox)

    def menu_main(self):
        def click_character():
            self.state = self.menu_character
            self.display(1)

        def click_skills():
            self.state = self.menu_skills
            self.display(1)

        def click_equipment():
            self.state = self.menu_equipment
            self.display(1)

        self.window.add_child(Menu.make_button(['Skills'], click_skills, None))
        self.window.add_child(Menu.make_button(['Character'], click_character, None))
        self.window.add_child(Menu.make_button(['Equipment'], click_equipment, None))

    def menu_character(self):
        def click_mastery():
            self.state = self.menu_mastery
            self.display(1)

        def click_status():
            self.state = self.menu_status
            self.display(1)

        def describe():
            self.show_dialog(['Something HP', 'Some long dialog text.....', 'And your choice'])

        hp = str(self.host.durability)
        text = ['HP - ' + hp + '/3', 'Str - 1', 'Agi - 1', 'Int - 1', 'Nutrition - 5/5']
        panel = Menu.make_button(text, describe, None)
        panel.color = Window.fore_color3
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.depth = 2
        panel.redraw()
        self.window.add_child(panel)
        self.sub_window.add_child(Menu.make_button(['Mastery'], click_mastery, None))
        self.sub_window.add_child(Menu.make_button(['Status'], click_status, None))
        self.sub_window.display(1)

    def menu_skills(self):
        def make_on_click(outer_index):
            def assign():
                def make_assign_click(inner_index):
                    def assign_click():
                        skills = self.host.action.skills
                        skills[outer_index], skills[inner_index] = skills[inner_index], skills[outer_index]
                        self.state = self.menu_skills
                        self.display(1)
                    return assign_click
                first = self.host.action.skills[:6]
                second = self.host.action.skills[6:]
                self.window.flush()
                for first_key, i in enumerate(first):
                    self.window.add_child(Menu.make_button([i.title()], make_assign_click(first_key), None))
                self.sub_window.flush()
                for second_key, i in enumerate(second):
                    self.sub_window.add_child(Menu.make_button([i.title()], make_assign_click(second_key + 6), None))
                self.window.display(1)
                self.sub_window.display(1)
            return assign
        control = Global.main.world.control
        key_buttons = []
        for k, v in control.keymap.items():
            if v[:3] == 'act':
                button = Menu.make_button(['Key [' + control.get_key_name(k) + ']'], None, None, color=(0, 0, 0, 0))
                button.hover_font_color = None
                key_buttons.append(button)
                self.window.add_child(button)
        abilities = self.host.action.skills[:6]
        for k, v in enumerate(abilities):
            action_button = Menu.make_button([v.title()], None, None)
            action_button.on_click = make_on_click(k)
            self.sub_window.add_child(action_button)
        self.sub_window.display(1)

    def menu_equipment(self):
        def click_headgear():
            if not self.host.unheadgear() and isinstance(self.host.weapon, Headgear):
                self.host.weapon.use(self.host)
            self.state = self.menu_equipment
            self.display(1)

        def click_armor():
            if not self.host.unarmor() and isinstance(self.host.weapon, Armor):
                self.host.weapon.use(self.host)
            self.state = self.menu_equipment
            self.display(1)

        def click_weapon():
            self.host.drop()
            self.state = self.menu_equipment
            self.display(1)

        def make_pocket(x, y):
            def pocket():
                if self.host.is_armed():
                    weapon = self.host.weapon
                    if self.host.armor.is_vacant(weapon, x, y):
                        self.host.drop()
                        weapon.remove()
                        self.host.armor.add_inventory(weapon, x, y)
                else:
                    item = self.host.armor.get_item_at(x, y, pop=1)
                    if item:
                        item.interact(self.host)
                self.state = self.menu_equipment
                self.display(1)
            return pocket

        self.window.add_child(Menu.make_button([self.host.headgear.name], click_headgear, None))
        self.window.add_child(Menu.make_button([self.host.armor.name], click_armor, None))
        self.window.add_child(Menu.make_button([self.host.weapon.name], click_weapon, None))
        for ky, vy in enumerate(self.host.armor.inventory):
            for kx, vx in enumerate(vy):
                if vx == Armor.VACANT:
                    color = Window.fore_color3
                elif vx == Armor.OCCUPIED:
                    color = (120, 120, 120, 220)
                else:
                    color = Window.fore_color0
                slot = Window([40, 40], color=color)
                slot.vec.x = kx * 48
                slot.vec.y = ky * 48
                slot.on_click = make_pocket(kx, ky)
                self.sub_window.next_y = self.sub_window.vec.y + 8
                self.sub_window.add_child(slot)
        inventory_items = self.host.armor.items
        for i in inventory_items:
            pos = (i.pos[0] * 48)
            pos.x += (48 * i.volume[0]) / 2
            pos.y += (48 * i.volume[1]) / 2
            item_canvas = CanvasWindow(i.form.name, vec=pos)
            self.sub_window.next_y = self.sub_window.vec.y + 8
            self.sub_window.add_child(item_canvas)
            item_canvas.display(1)
        textbox = Window([140, 0], color=Window.fore_color3)
        textbox.hover_font_color = Window.fore_color3
        textbox.set_text(['Gold: ' + str(self.host.gold)])
        self.window.add_child(textbox)
        self.sub_window.display(1)

    def menu_mastery(self):
        self.window.add_child(Menu.make_button(['Mastery'], None, None))

    def menu_status(self):
        for i in self.host.states.buffs:
            self.window.add_child(Menu.make_button([i[1].title()], None, None, color=Window.fore_color0))
            self.sub_window.add_child(Menu.make_button([str(i[2])], None, None, color=Window.fore_color0))
        self.sub_window.display(1)
