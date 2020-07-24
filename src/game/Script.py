from src.entity.Particle import Particle
from src.game import Global
from src.tools.Data import Data
from src.tools.Dialog import Dialog
from src.tools.Random import Random


class Script:
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
        self.condition = None
        self.mechanism = None
        self.exception = None
        self.rand = None

    def __str__(self):
        string = Dialog.deepnonstrlist
        return string(self.condition, 2) + ',' + string(self.mechanism, 2) + ',' + string(self.exception, 2)

    def load(self, arg):
        index = 0
        self.condition = arg[index]
        index += 1
        self.mechanism = arg[index]
        index += 1
        self.exception = arg[index]
        return index + 1

    def run(self):
        for i in self.condition:
            if not self.run_condition(i):
                self.run_exceptions()
                return
        self.run_mechanisms()
        return True

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
            elif arg[2] == 'split':
                Script.var[str(arg[1])] = arg[3].split(arg[4])
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
        elif condition[0] == 'bring':
            return Script.var['host'].pos == Global.player.character.pos
        elif condition[0] == 'delay':
            return Script.var['1'].action.delay == 0
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
            Script.var['host'].location.sound.register(Script.var['host'].pos, arg[1], file=arg[2])
        elif arg[0] == 'closemenu':
            Global.menu.display(-1)
        elif arg[0] == 'message':
            Global.menu.get_message(arg[1])()
        elif arg[0] == 'dialog':
            Global.menu.topic(arg[1:])
        elif arg[0] == 'say':
            Global.main.monologue.set(arg[1])
        elif arg[0] == 'remove':
            arg[1].remove()
        elif arg[0] == 'spell':
            from src.entity.unit.item.Spell import Spell
            Spell.perform(Script.var['host'].pos, arg[1])
        elif arg[0] == 'buff':
            Script.var['host'].states.add(arg[1], arg[2], var=arg[3])
        elif arg[0] == 'time':
            Global.player.days = arg[1]
            Global.map_view.overlay.blackout()
            Global.player.sleep(0)
        elif arg[0] == 'menu':
            Global.menu.var = Script.var['1']
            Global.menu.direct(getattr(Global.menu, 'menu_' + arg[1].lower()))
        elif arg[0] == 'script':
            Script.execute_code(arg[1])
        elif arg[0] == 'decay':
            Script.var['1'].decay(arg[1])
        elif arg[0] == 'act':
            from src.entity.unit.Unit import Unit
            if isinstance(Script.var['host'], Unit):
                if arg[1] == 'act':
                    Script.var['host'].action.act(arg[2], arg[3])
                else:
                    Script.var['host'].action.set(arg[1])
        elif arg[0] == 'move':
            from src.entity.Other import Scripter
            host_pos = Script.var['host'].pos
            for i in host_pos.things:
                if not isinstance(i, Scripter):
                    i.relocate(x=host_pos.x + arg[1], y=host_pos.y + arg[2], force=True)
        elif arg[0] == 'forward':
            host = Script.var['host']
            host.relocate(to=host.pos.get_cardinal(host.direction, arg[1]))
        elif arg[0] == 'teleport':
            Global.world.travel(arg[1], arg[2])
        elif arg[0] == 'sleep':
            Global.player.sleep(arg[1])
        elif arg[0] == 'deletefiles':
            Data.delete_all()
