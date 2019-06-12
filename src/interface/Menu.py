import pygame

from src.entity.unit.item.Armor import Armor
from src.entity.unit.item.Headgear import Headgear
from src.game import Global
from src.game.Crafting import Crafting
from src.game.Turn import Turn
from src.interface.CanvasWindow import CanvasWindow
from src.interface.Window import Window


class Menu:
    def __init__(self, host):
        Turn.add(self)
        self.host = host
        self.visible = -1
        self.state = self.menu_main
        self.current_state = self.menu_main
        self.window = Window([160, 300], (300, 120))
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
    def make_button(text, callback, r_callback, color=Window.fore_color2):
        button = Window([140, 40], color=color)
        button.set_text(text)
        button.on_click = callback
        button.on_r_click = r_callback
        return button

    def show_dialog(self, text):
        r = []
        for line in text:
            length = 0
            newline = ''
            for char in line:
                newline += char
                length += self.window.font.size(char)[0]
                if length >= self.window.size.x + self.sub_window.size.x - self.window.margin.x * 5:
                    r.append(newline)
                    newline = ''
                    length = 0
            r.append(newline)
        self.dialog_text = r
        self.direct(self.menu_dialog)

    def menu_dialog(self):
        x = self.window.size.x + self.sub_window.size.x - self.window.margin.x * 2
        textbox = Window([x, 1], color=Window.fore_color2)
        textbox.text_spacing = textbox.font.size('A')[1] + 2
        textbox.set_text(self.dialog_text + [' '])
        textbox.hover_font_color = textbox.normal_font_color
        self.window.add_child(textbox)
        self.sub_window.display(1)

    def menu_main(self):
        def click_character():
            self.direct(self.menu_character)

        def click_equipment():
            self.direct(self.menu_equipment)

        def click_knowledge():
            self.direct(self.menu_knowledge)

        self.window.add_child(Menu.make_button(['Character'], click_character, None))
        self.window.add_child(Menu.make_button(['Equipment'], click_equipment, None))
        self.window.add_child(Menu.make_button(['Knowledge'], click_knowledge, None))

    def menu_character(self):
        def click_proficiency():
            self.direct(self.menu_proficiency)

        def click_status():
            self.direct(self.menu_status)

        def describe():
            self.show_dialog(['Something HP', 'Some long dialog text.....', 'And your choice'])

        hp = str(self.host.durability)
        st1 = str(self.host.attributes.strength)
        st2 = str(self.host.attributes.agility)
        st3 = str(self.host.attributes.intelligence)
        text = ['HP - ' + hp, 'Str - ' + st1, 'Agi - ' + st2, 'Int - ' + st3]
        panel = Menu.make_button(text, describe, None)
        panel.color = Window.fore_color3
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add_child(panel)
        self.sub_window.add_child(Menu.make_button(['Proficiency'], click_proficiency, None))
        self.sub_window.add_child(Menu.make_button(['Status'], click_status, None))
        self.sub_window.display(1)

    def menu_knowledge(self):
        def add_button(window, text):
            def craft():
                Crafting.craft(self.host, text)
                self.host.action.set('block')
                self.toggle()
            if Crafting.is_craftable(self.host, text):
                rmb = self.get_message(Crafting.describe(text).split('\n'))
                button = Menu.make_button([text], craft, rmb)
            else:
                rmb = self.get_message((Crafting.describe(text) + '\nRequirements not met.').split('\n'))
                button = Menu.make_button([text], None, rmb, color=Window.fore_color0)
                button.hover_font_color = window.normal_font_color
            window.add_child(button)

        for i in Global.main.player.knowledge[:6]:
            add_button(self.window, i)
        for i in Global.main.player.knowledge[6:]:
            add_button(self.sub_window, i)
        self.window.display(1)
        self.sub_window.display(1)

    def menu_skills(self):
        def make_on_click(outer_index):
            def assign():
                self.var = outer_index
                self.direct(self.menu_slot_reassign)
            return assign
        control = Global.main.player.control
        key_buttons = []
        for k, v in control.keymap.items():
            if v[:4] == 'item':
                button = Menu.make_button(['Key [' + control.get_key_name(k) + ']'], None, None, color=(0, 0, 0, 0))
                button.hover_font_color = None
                key_buttons.append(button)
                self.window.add_child(button)
        for k, v in enumerate(self.host.armor.pockets):
            if v == -1:
                desc = self.get_message(['Click to assign item.'])
                action_button = Menu.make_button(['<Assign>'], make_on_click(k), desc)
            else:
                action_button = Menu.make_button([self.host.armor.items[v].name], make_on_click(k), None)
            self.sub_window.add_child(action_button)
        self.sub_window.display(1)

    def menu_slot_reassign(self):
        def make_assign_click(inner_index):
            def assign_click():
                self.host.armor.pockets[self.var] = inner_index
                self.direct(self.menu_skills)
            return assign_click
        first = self.host.armor.items[:6]
        second = self.host.armor.items[6:]
        self.window.flush()
        for first_key, i in enumerate(first):
            self.window.add_child(Menu.make_button([i.name], make_assign_click(first_key), None))
        self.sub_window.flush()
        for second_key, i in enumerate(second):
            self.sub_window.add_child(Menu.make_button([i.name], make_assign_click(second_key + 6), None))
        self.window.display(1)
        self.sub_window.display(1)

    def menu_equipment(self):
        def click_headgear():
            if not self.host.unheadgear() and isinstance(self.host.weapon, Headgear):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        def click_armor():
            if not self.host.unarmor() and isinstance(self.host.weapon, Armor):
                self.host.weapon.use()
            self.direct(self.menu_equipment)

        def click_offhand():
            self.host.swap()
            self.direct(self.menu_equipment)

        def click_weapon():
            self.host.drop()
            self.direct(self.menu_equipment)

        def make_pocket(x, y):
            def pocket():
                if self.host.is_armed():
                    weapon = self.host.weapon
                    if self.host.armor.is_vacant(weapon, x, y):
                        self.host.drop()
                        self.host.armor.add_inventory(weapon, x, y)
                else:
                    item = self.host.armor.get_item_at(x, y, pop=1)
                    if item:
                        item.on_equip(self.host)
                self.state = self.menu_equipment
                self.display(1)
            return pocket

        def make_pocket_desc(x, y):
            def pocket():
                item = self.host.armor.get_item_at(x, y)
                if item:
                    self.show_dialog(item.describe().split('\n'))
            return pocket

        def click_skills():
            self.direct(self.menu_skills)

        rmb = self.get_message(self.host.headgear.describe().split('\n'))
        self.window.add_child(Menu.make_button([self.host.headgear.name], click_headgear, rmb))
        rmb = self.get_message(self.host.armor.describe().split('\n'))
        self.window.add_child(Menu.make_button([self.host.armor.name], click_armor, rmb))
        if len(self.host.armor.pockets) > 0:
            rmb = self.get_message(['Designate items for quick access.'])
            button = Menu.make_button(['Pockets'], click_skills, rmb, color=Window.fore_color3)
        else:
            button = Menu.make_button([''], None, None, color=(0, 0, 0, 0))
        self.window.add_child(button)
        rmb = self.get_message(self.host.offhand.describe().split('\n'))
        display = self.host.offhand.name
        if not self.host.is_shielded():
            display = '<Offhand>'
        self.window.add_child(Menu.make_button([display], click_offhand, rmb))
        rmb = self.get_message(self.host.weapon.describe().split('\n'))
        display = self.host.weapon.name
        if not self.host.is_armed():
            display = '<Unarmed>'
        self.window.add_child(Menu.make_button([display], click_weapon, rmb))
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
                slot.on_r_click = make_pocket_desc(kx, ky)
                self.sub_window.next_y = self.sub_window.vec.y + 8
                self.sub_window.add_child(slot)
        inventory_items = self.host.armor.items
        for i in inventory_items:
            pos = (i.pos[0] * 48)
            pos.x += (48 * i.volume[0]) / 2
            pos.y += (48 * i.volume[1]) / 2
            pos.x -= (i.form.size.x/2 - i.form.pivot.x)
            pos.y -= (i.form.size.y/2 - i.form.pivot.y)
            item_canvas = CanvasWindow(i.form, vec=pos)
            self.sub_window.next_y = self.sub_window.vec.y + 8
            self.sub_window.add_child(item_canvas)
            item_canvas.display(1)
        self.sub_window.display(1)

    def menu_proficiency(self):
        count = 0
        for i in self.host.proficiency:
            button = Menu.make_button([i.title()], None, None)
            if count < 6:
                self.window.add_child(button)
            else:
                self.sub_window.add_child(button)
            count += 1
        self.sub_window.display(1)

    def menu_status(self):
        for i in self.host.states.buffs:
            rmb = self.get_message(i.describe().split('\n'))
            self.window.add_child(Menu.make_button([i.name.title()], rmb, rmb, color=Window.fore_color0))
            if i.duration == -1:
                dur = 'Persistent'
            else:
                dur = str(i.duration)
            self.sub_window.add_child(Menu.make_button([dur], None, None, color=Window.fore_color0))
        self.sub_window.display(1)

    def get_message(self, msg):
        def message():
            self.show_dialog(msg)
        return message
