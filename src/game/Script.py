from src.entity.Particle import Particle
from src.game import Global
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Script:
    NONE = 0
    ONCE = 1
    MAKE = 2
    TURN = 3

    @staticmethod
    def execute_string(arg, host=None, var=None):
        new = Script(host)
        new.load(arg)
        new.var = var
        new.run()

    @staticmethod
    def execute_line(arg, host=None, var=None):
        data = Data.get_line('script.txt', arg.lower())
        if data:
            Script.execute_string(data[1:], host, var)
            return True

    @staticmethod
    def execute_code(arg, host=None, var=None):
        if arg:
            if arg.startswith('!'):
                Global.menu.topic(arg[1:])
                return True
            elif arg.startswith('#'):
                from src.game.ScriptManual import ScriptManual
                ScriptManual.execute(arg[1:], host, var)
                return True
            return Script.execute_line(arg, host, var)

    def __init__(self, host=None):
        self.period = Script.NONE
        self.condition = None
        self.mechanism = None
        self.exception = None
        from src.tools.Random import Random
        self.rand = Random(0)
        self.host = host or Global.player.character
        self.var = None

    def __str__(self):
        string = Dialog.deepnonstrlist
        cnm = string(self.condition, 2) + ',' + string(self.mechanism, 2) + ',' + string(self.exception, 2)
        return str(self.period) + ',' + cnm

    def load(self, arg):
        index = 0
        self.period = arg[index]
        index += 1
        self.condition = arg[index]
        index += 1
        self.mechanism = arg[index]
        index += 1
        self.exception = arg[index]
        return index + 1

    def turn(self):
        self.run_script()

    def run(self):
        if self.period == Script.ONCE:
            self.run_script()
            self.period = Script.NONE
        elif self.period == Script.TURN:
            from src.game.Turn import Turn
            Turn.add(self.turn)

    def remove(self):
        from src.game.Turn import Turn
        Turn.remove(self)
        del self

    def run_script(self):
        for i in self.condition:
            if not self.run_condition(i):
                self.run_exceptions()
                return
        self.run_mechanisms()

    def run_mechanisms(self):
        for i in self.mechanism:
            self.run_mechanism(i)

    def run_exceptions(self):
        for i in self.exception:
            self.run_mechanism(i)

    def run_preposition(self, arg):
        if arg[0] == '=':
            if arg[1] == '=':
                self.var = arg[2]
            elif arg[1] == 'where':
                self.var = [self.host.pos.x, self.host.pos.y]
            elif arg[1] == 'raw':
                self.var = Data.get_line(arg[2] + '.txt', arg[3].lower())
            elif arg[1] == 'array':
                self.var = arg[2][arg[3]]
            elif arg[1] == 'player':
                self.host = Global.player.character
            elif arg[1] == 'host':
                self.host = self.var
            elif arg[1] == '?list':
                self.var = self.rand.rand_list(arg[2])
            elif arg[1] == '?int':
                self.var = self.rand.rand_int(arg[2], arg[3])
            elif arg[1] == '+':
                if isinstance(arg[2], str) or isinstance(arg[3], str):
                    self.var = str(arg[2]) + str(arg[3])
                else:
                    self.var = arg[2] + arg[3]
            elif arg[1] == 'time':
                self.var = Global.player.days
                Global.player.set_darkness()
            elif arg[1] == 'maptag':
                self.var = Global.land.tags.get(arg[2])
            elif arg[1] == 'hosttag':
                self.var = self.host.tags.get(arg[2])
            elif arg[1] == 'skill':
                self.var = self.host.get_skill(arg[2])
            elif arg[1] == 'gethost':
                self.var = self.host
        elif arg[0] == 'v':
            if arg[1] == '=':
                Global.land.tags.set(arg[2], arg[3], add=True)
            elif arg[1] == '+':
                Global.land.tags.increment(arg[2], arg[3])
            elif arg[1] == 'remove':
                Global.land.tags.remove(arg[2])
        elif arg[0] == 'h':
            if arg[1] == '=':
                self.host.tags.set(arg[2], arg[3], add=True)
            elif arg[1] == '+':
                self.host.tags.increment(arg[2], arg[3])
            elif arg[1] == 'remove':
                self.host.tags.remove(arg[2])
        else:
            return False
        return True

    def replace_variable(self, arg):
        new = []
        for i in arg:
            if isinstance(i, str):
                if i == '*':
                    new.append(self.var)
                # elif i.startswith('#'):
                #     new.append(self.var[int(i[1])])
                else:
                    new.append(i)
            elif isinstance(i, list):
                nest = []
                for ii in i:
                    if isinstance(ii, str):
                        if i == '*':
                            new.append(self.var)
                        # elif ii.startswith('#'):
                        #     nest.append(self.var[int(ii[1])])
                        else:
                            nest.append(ii)
                    else:
                        nest.append(ii)
                new.append(nest)
            else:
                new.append(i)
        return new

    def run_condition(self, condition):
        condition = self.replace_variable(condition)
        if condition[0].startswith('!'):
            condition[0] = condition[0][1:]
            return not self.run_condition(condition)
        elif self.run_preposition(condition):
            return True
        elif condition[0] == 'equal':
            if self.var == condition[1]:
                return True
        elif condition[0] == 'greater':
            if self.var > condition[1]:
                return True
        elif condition[0] == 'date':
            if Global.player.days > condition[1]:
                condition[1] = Global.player.days + condition[2]
                return True
        elif condition[0] == 'limit':
            condition[1] -= 1
            if condition[1] == 0:
                return True
        elif condition[0] == 'safe':
            return Global.player.is_safe()
        elif condition[0] == 'bright':
            return Global.player.is_bright()
        elif condition[0] == 'delay':
            return self.host.action.delay == 0
        elif condition[0] == 'inmenu':
            return Global.menu.visible == 1
        elif condition[0] == 'ask':
            def on_yes(name):
                Global.menu.toggle()
                for cnd in self.condition[self.condition.index(condition) + 1:]:
                    if not self.run_condition(cnd):
                        if len(condition) > 3:
                            Script.execute_code(condition[3])
                        return
                self.run_mechanisms()
            Global.menu.get_prompt(condition[1], condition[2], on_yes, 0)(None)
            return False

    def run_mechanism(self, arg):
        arg = self.replace_variable(arg)
        if self.run_preposition(arg):
            pass
        elif arg[0] == 'exit':
            Global.player.control.quit()
        elif arg[0] == 'script':
            if len(arg) > 2:
                Script.execute_line(arg[1], arg[2])
            else:
                Script.execute_line(arg[1])
        elif arg[0] == 'save':
            Data.write('data/raw/' + arg[1] + '.txt', arg[2])
        elif arg[0] == 'spawn':
            from src.entity.Stock import Stock
            Stock.make(arg[1], self.host.pos)
        elif arg[0] == 'effect':
            Particle.make(arg[1], self.host.pos.get_center(), offset=8)
        elif arg[0] == 'toggle':
            Global.menu.toggle()
        elif arg[0] == 'message':
            Global.menu.get_message(arg[1])(None)
        elif arg[0] == 'dialog':
            Global.menu.topic(arg[1:])
        elif arg[0] == 'say':
            Global.main.monologue.set(arg[1])
        elif arg[0] == 'removeat':
            for thing in self.host.pos.things.copy():
                if thing != self.host:
                    thing.remove()
        elif arg[0] == 'removeself':
            self.remove()
            self.host.remove()
        elif arg[0] == 'trigger':
            self.var.trigger()
        elif arg[0] == 'spell':
            from src.entity.unit.item.Spell import Spell
            Spell.perform(self.host, arg[1])
        elif arg[0] == 'hit':
            for thing in self.var:
                thing.hit(arg[2])
        elif arg[0] == 'buff':
            self.host.states.add(arg[1], arg[2], var=arg[3])
        elif arg[0] == 'relocate':
            for thing in self.var:
                thing.relocate(arg[2], arg[3])
        elif arg[0] == 'move':
            for thing in self.var:
                thing.move(arg[2], arg[3])
        elif arg[0] == 'thief':
            from src.entity.unit.item.Item import Item
            for i in Global.land.population.other:
                if isinstance(i, Item):
                    if i.get_value() >= arg[1]:
                        i.remove()
        elif arg[0] == 'sepia':
            Global.map_view.overlay.colorize([arg[1], arg[2], arg[3], arg[4]])
        elif arg[0] == 'blackout':
            Global.map_view.overlay.blackout()
        elif arg[0] == 'darkness':
            Global.land.view_range = arg[1]
            Global.land.sight_range = arg[2]
            Global.player.set_darkness()
        elif arg[0] == 'time':
            Global.player.days = arg[1]
            Global.map_view.overlay.blackout()
            Global.player.sleep(0)
        elif arg[0] == 'enter':
            if len(arg) == 2:
                Global.player.travel(arg[1])
            else:
                Global.player.travel(arg[1], arg[2], arg[3])
        elif arg[0] == 'menu':
            Global.menu.var = self.var
            Global.menu.direct(getattr(Global.menu, 'menu_' + arg[1].lower()))
        elif arg[0] == 'script':
            from src.game.ScriptManual import ScriptManual
            ScriptManual.execute(arg[1], self.host, self.var)
        elif arg[0] == 'flip':
            Global.land.flip(arg[1], arg[2])
        elif arg[0] == 'rotate':
            Global.land.rotate()
            Global.map_view.on_sight_change()
        elif arg[0] == 'load':
            building = Data.process_raw(Data.read(arg[2] + '.map'))
            from src.map.Location import Location
            location = Location(arg[1], building, make=True)
            location.save()
        elif arg[0] == 'merge':
            building = Data.process_raw(Data.read(arg[2] + '.map'))
            from src.map.Location import Location
            location = Location(arg[1], building, make=True)
            building = Data.process_raw(Data.read(arg[3] + '.map'))
            location.load(building, offset=[arg[4], arg[5]], make=True)
            location.save()
        elif arg[0] == 'generate':
            from src.map.Generator import Generator
            generator = Generator.get(arg[2])(arg[3], arg[4])
            location = generator.run(arg[1])
            location.save()
        elif arg[0] == 'unwield':
            Global.player.character.weapon.remove()
        elif arg[0] == 'delay':
            from src.entity.unit.Unit import Unit
            if isinstance(self.host, Unit):
                self.host.action.delay = arg[1]
        elif arg[0] == 'act':
            from src.entity.unit.Unit import Unit
            if isinstance(self.host, Unit) and self.host.action.delay == 0:
                if arg[1] == 'act':
                    self.host.action.act(arg[2], arg[3])
                else:
                    self.host.action.set(arg[1])
        elif arg[0] == 'sleep':
            Global.player.sleep(arg[1])
