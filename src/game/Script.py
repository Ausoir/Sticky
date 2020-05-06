from src.entity.Particle import Particle
from src.game import Global
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Random import Random


class Script:
    NONE = 0
    ONCE = 1
    MAKE = 2
    TURN = 3
    var = {'1': None, 'fail': 0}

    @staticmethod
    def execute_string(arg):
        new = Script()
        new.load(arg)
        new.run()

    @staticmethod
    def execute_line(arg):
        data = Data.get_line('script.txt', arg.lower())
        if data:
            Script.execute_string(data[1:])
            return True

    @staticmethod
    def execute_code(arg):
        if arg:
            Global.player.control.clear_press()
            if arg.startswith('!'):
                Global.menu.load(arg[1:])
                return True
            elif arg.startswith('#'):
                from src.game.ScriptManual import ScriptManual
                ScriptManual.execute(arg[1:], Script.var['host'], Script.var['1'])
                return True
            elif arg.startswith('>'):
                Script().run_mechanism(Data.parse(arg[1:].replace('>', ',')))
                return True
            return Script.execute_line(arg)

    @staticmethod
    def replace_variable(arg):
        new = []
        for i in arg:
            if isinstance(i, str):
                if i.startswith('*'):
                    new.append(Script.var[i[1:]])
                else:
                    new.append(i)
            elif isinstance(i, list):
                nest = []
                for ii in i:
                    if isinstance(ii, str):
                        if ii.startswith('*'):
                            new.append(Script.var[i[1:]])
                        else:
                            nest.append(ii)
                    else:
                        nest.append(ii)
                new.append(nest)
            else:
                new.append(i)
        return new

    def __init__(self):
        self.period = Script.NONE
        self.condition = None
        self.mechanism = None
        self.exception = None
        self.rand = None

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

    def get_rand(self):
        if not self.rand:
            self.rand = Random(Script.var['host'].tags.get('seed', Global.r.rand_int(0, 9999)))
        return self.rand

    def run_preposition(self, arg):
        if arg[0] == '=':
            Script.var[str(arg[1])] = arg[2]
        elif arg[0] == 'v':
            if arg[2] == 'raw':
                Script.var[str(arg[1])] = Data.get_line(arg[3] + '.txt', arg[4].lower())
            elif arg[2] == 'array':
                Script.var[str(arg[1])] = arg[3][arg[4]]
            elif arg[2] == '?list':
                Script.var[str(arg[1])] = self.get_rand().rand_list(arg[3])
            elif arg[2] == '?int':
                Script.var[str(arg[1])] = self.get_rand().rand_int(arg[3], arg[4])
            elif arg[2] == '+':
                if isinstance(arg[3], str) or isinstance(arg[4], str):
                    Script.var[str(arg[1])] = str(arg[3]) + str(arg[4])
                else:
                    Script.var[str(arg[1])] = arg[3] + arg[4]
            elif arg[2] == 'x':
                Script.var[str(arg[1])] = int(float(arg[3]) * float(arg[4]))
            elif arg[2] == 'time':
                Script.var[str(arg[1])] = Global.player.days
                Global.player.set_darkness()
            elif arg[2] == 'map':
                Script.var[str(arg[1])] = arg[3].location
            elif arg[2] == 'tag':
                Script.var[str(arg[1])] = arg[3].tags.get(arg[4], Script.var['fail'])
            elif arg[2] == 'skill':
                Script.var[str(arg[1])] = Script.var[str(arg[1])].get_skill(arg[3], stacks=True)
            elif arg[2] == 'settag':
                Script.var[str(arg[1])].tags.set(arg[3], arg[4])
            elif arg[2] == 'addtag':
                Script.var[str(arg[1])].tags.increment(arg[3], arg[4])
            elif arg[2] == 'deltag':
                Script.var[str(arg[1])].tags.remove(arg[3])
        else:
            return False
        return True

    def run_condition(self, condition):
        condition = Script.replace_variable(condition)
        if condition[0].startswith('!'):
            condition[0] = condition[0][1:]
            return not self.run_condition(condition)
        elif self.run_preposition(condition):
            return True
        elif condition[0] == 'equal':
            return Script.var['1'] == condition[1]
        elif condition[0] == 'greater':
            return Script.var['1'] > condition[1]
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
            return Script.var[1].action.delay == 0
        elif condition[0] == 'inmenu':
            return Global.menu.visible == 1
        elif condition[0] == 'ask':
            def on_yes(name):
                for cnd in self.condition[self.condition.index(condition) + 1:]:
                    if not self.run_condition(cnd):
                        if len(condition) > 3:
                            Script.execute_code(condition[3])
                        return
                self.run_mechanisms()
            Global.menu.get_prompt(condition[1], condition[2], on_yes)()
            return False

    def run_mechanism(self, arg):
        arg = Script.replace_variable(arg)
        if self.run_preposition(arg):
            pass
        elif arg[0] == 'exit':
            Global.main.quit()
        elif arg[0] == 'script':
            Script.execute_code(arg[1])
        elif arg[0] == 'save':
            Data.write('data/raw/' + arg[1] + '.txt', arg[2])
        elif arg[0] == 'spawn':
            from src.entity.Stock import Stock
            Script.var['1'] = Stock.make(arg[1], Script.var['host'].pos)
        elif arg[0] == 'effect':
            Particle.make(arg[1], Script.var['host'].pos, offset=8)
        elif arg[0] == 'sound':
            Script.var['host'].location.sound.register(Script.var['host'].pos, arg[2], file=arg[1])
        elif arg[0] == 'closemenu':
            Global.menu.display(-1)
        elif arg[0] == 'message':
            Global.menu.get_message(arg[1])()
        elif arg[0] == 'dialog':
            Global.menu.topic(arg[1:])
        elif arg[0] == 'say':
            Global.main.monologue.set(arg[1])
        elif arg[0] == 'removeat':
            for thing in Script.var['host'].pos.things.copy():
                if thing != Script.var['host']:
                    thing.remove()
        elif arg[0] == 'remove':
            self.remove()
            arg[1].remove()
        elif arg[0] == 'trigger':
            Script.var['1'].trigger()
        elif arg[0] == 'spell':
            from src.entity.unit.item.Spell import Spell
            Spell.perform(Script.var['host'], arg[1])
        elif arg[0] == 'buff':
            Script.var['host'].states.add(arg[1], arg[2], var=arg[3])
        elif arg[0] == 'darkness':
            Global.land.set_view_range(arg[1])
            Global.land.set_sight_range(arg[2])
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
            Global.menu.var = Script.var['1']
            Global.menu.direct(getattr(Global.menu, 'menu_' + arg[1].lower()))
        elif arg[0] == 'script':
            Script.execute_code(arg[1])
        elif arg[0] == 'new':
            building = Data.process_raw(Data.read(arg[2] + '.map'))
            from src.map.Location import Location
            location = Location(arg[1], building, make=True)
            location.save()
        elif arg[0] == 'load':
            building = Data.process_raw(Data.read(arg[1] + '.map'))
            host = Script.var['host']
            Global.land.load(building, offset=[arg[2], arg[3]], make=True)
            Script.var['host'] = host
        elif arg[0] == 'loadhere':
            host = Script.var['host']
            building = Data.process_raw(Data.read(arg[1] + '.map'))
            from src.map.Location import Location
            location = Location('', building, make=True)
            location.rotate(self.get_rand().rand_int(0, 3))
            data = Data.process_raw(location.__str__())
            Script.var['host'] = host
            offset = [Script.var['host'].pos.x, Script.var['host'].pos.y]
            Script.var['host'].location.load(data, offset=offset, make=True)
        elif arg[0] == 'merge':
            host = Script.var['host']
            building = Data.process_raw(Data.read(arg[2] + '.map'))
            from src.map.Location import Location
            location = Location(arg[1], building, make=True)
            building = Data.process_raw(Data.read(arg[3] + '.map'))
            location.load(building, offset=[arg[4], arg[5]], make=True)
            location.save()
            Script.var['host'] = host
        elif arg[0] == 'generate':
            from src.map.Generator import Generator
            generator = Generator.get(arg[2])(arg[3], arg[4])
            location = generator.run(arg[1])
            location.save()
        elif arg[0] == 'template':
            from src.map.Generator import Generator
            location = Generator.get_template(arg[1], arg[2], self.get_rand().rand_rand())
            location.save()
        elif arg[0] == 'unwield':
            Global.player.character.weapon.remove()
        elif arg[0] == 'delay':
            from src.entity.unit.Unit import Unit
            if isinstance(Script.var['host'], Unit):
                Script.var['host'].action.delay = arg[1]
        elif arg[0] == 'act':
            from src.entity.unit.Unit import Unit
            if isinstance(Script.var['host'], Unit) and Script.var['host'].action.delay == 0:
                if arg[1] == 'act':
                    Script.var['host'].action.act(arg[2], arg[3])
                else:
                    Script.var['host'].action.set(arg[1])
        elif arg[0] == 'sleep':
            Global.player.sleep(arg[1])
