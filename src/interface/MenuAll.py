from src.game import Global
from src.interface.Menu import Menu
from src.interface.MenuPlayer import MenuPlayer
from src.interface.Window import Window


class MenuAll(MenuPlayer):
    def menu_travel(self):
        self.history = [self.menu_travel]
        if Global.main.player.character.states.get('Hunger'):
            self.show_dialog(['You are too hungry to travel!', 'Eat something first.'])
        else:
            text = ['Choose your', 'destination.']
            panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False)
            panel.normal_font_color = Window.font_color1
            panel.hover_font_color = Window.font_color3
            panel.redraw()
            self.window.add_child(panel)
            from src.entity.Space import Space
            for i in self.var:
                def click():
                    self.host.states.add('Hunger', -1)
                    Global.main.player.travel(i[0], Space(int(i[1]), int(i[2])))
                rmb = self.get_message(['Travel to ' + i[0].title()])
                self.sub_window.add_child(Menu.make_button([i[0].title()], click, rmb))
            self.sub_window.display(1)

    def menu_shop(self):
        self.history = [self.menu_shop]
        from src.entity.Stock import Stock
        for i in self.var:
            item = Stock.get(i)
            gold = str(item.get_value()) + ' Gold'
            rmb = self.get_message(item.describe().split('\n'))

            def onclick():
                if Global.main.player.character.modify_gold(-item.get_value()):
                    item.relocate(Global.main.player.character.pos[0].x, Global.main.player.character.pos[0].y, force=1)
                    item.add()
            self.window.add_child(Menu.make_button([i], onclick, rmb))
            self.sub_window.add_child(Menu.make_button([gold], None, rmb, color=Window.fore_color0, hover=False))
        self.sub_window.display(1)

    def menu_trainer(self):
        def click(stat, sessions):
            def training():
                if not self.host.states.get('Hunger'):
                    Global.main.player.sleep(1)
                    self.host.states.add('Hunger', -1)
                    if sessions <= 1:
                        Global.main.player.experience[stat] = 0
                        if stat == 0:
                            Global.main.player.character.attributes.strength += 1
                        elif stat == 1:
                            Global.main.player.character.attributes.agility += 1
                        Global.main.monologue.text('Completed current training!')
                    else:
                        Global.main.player.experience[stat] += 1
                        Global.main.monologue.text('Completed a training session.')
                    self.toggle()
                else:
                    self.show_dialog(['You are too hungry to train!', 'Eat something first.'])
            return training
        self.history = [self.menu_trainer]
        text = ['Welcome home.', 'Hone your skills', 'while you can.']
        panel = Menu.make_button(text, None, None, color=Window.fore_color0, hover=False)
        panel.normal_font_color = Window.font_color1
        panel.hover_font_color = Window.font_color3
        panel.redraw()
        self.window.add_child(panel)
        cost = Global.main.player.character.attributes.strength - Global.main.player.experience[0]
        rmb = self.get_message(['Increase Strength. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add_child(Menu.make_button(['Strength'], click(0, cost), rmb))
        cost = Global.main.player.character.attributes.agility - Global.main.player.experience[1]
        rmb = self.get_message(['Increase Agility. Takes ' + str(cost) + ' sessions.'])
        self.sub_window.add_child(Menu.make_button(['Agility'], click(1, cost), rmb))
        self.sub_window.display(1)
