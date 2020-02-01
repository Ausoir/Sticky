from src.entity.Other import Scripter
from src.entity.Particle import Particle
from src.game import Global
from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Script:
    NONE = 0
    ONCE = 1
    MANUAL = 2
    TURN = 3
    MAKE = 4

    @staticmethod
    def execute_string(arg, host=None):
        new = Script(host)
        new.load(arg)
        new.run()

    @staticmethod
    def execute_line(arg, host=None):
        data = Data.get_line('raw/script.txt', arg.lower())
        if data:
            Script.execute_string(data[1:], host)
            return True

    @staticmethod
    def execute_code(arg, host=None):
        if arg:
            if arg.startswith('!'):
                Global.menu.topic(arg[1:])
                return True
            return Script.execute_line(arg, host)

    def __init__(self, host=None):
        self.period = Script.NONE
        self.condition = None
        self.mechanism = None
        self.exception = None
        self.seed = None
        self.rand = None
        self.var = [host or Global.player.character, None, None, None, None]

    def __str__(self):
        string = Dialog.deepnonstrlist
        cnm = string(self.condition, 2) + ',' + string(self.mechanism, 2) + ',' + string(self.exception, 2)
        return str(self.period) + ',' + str(self.seed) + ',' + cnm

    def load(self, arg):
        index = 0
        self.period = arg[index]
        index += 1
        self.seed = arg[index]
        from src.tools.Random import Random
        self.rand = Random(self.seed)
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
        elif self.period == Script.MANUAL:
            self.run_script()
        elif self.period == Script.TURN:
            from src.game.Turn import Turn
            Turn.add(self.turn)

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

    def run_preposition(self, segment, arg):
        if arg[0].startswith('='):
            what = None
            if arg[1] == '=':
                what = arg[2]
            elif arg[1] == 'where':
                what = self.var[0].location.get_tile([arg[2], arg[3]]).things
            elif arg[1] == 'wherer':
                what = self.var[0].location.get_tile([self.var[0].pos.x + arg[2], self.var[0].pos.y + arg[3]]).things
            elif arg[1] == 'raw':
                what = Data.get_line('raw/' + arg[2] + '.txt', arg[3].lower())
            elif arg[1] == 'array':
                what = arg[2][arg[3]]
            elif arg[1] == 'name':
                what = []
                for i in arg[2]:
                    if i.name == arg[3]:
                        what.append(i)
            elif arg[1] == '!name':
                what = []
                for i in arg[2]:
                    if i.name != arg[3]:
                        what.append(i)
            elif arg[1] == 'player':
                what = [Global.player.character]
            elif arg[1] == '?list':
                r = []
                for i in range(arg[3]):
                    r.append(self.rand.rand_list(arg[2]))
                what = r
            elif arg[1] == '?int':
                what = self.rand.rand_int(arg[2], arg[3])
            self.var[int(arg[0][1])] = what
        elif arg[0] == 'seed':
            if arg[1] == 'timespace':
                self.var = Global.player.days * Global.player.character.location.seed
            elif arg[1] == 'hostgene':
                self.var = self.var[0].attributes.gene
            else:
                self.seed = arg[1]
            from src.tools.Random import Random
            self.rand = Random(self.seed)
        else:
            return False
        return True

    def replace_variable(self, arg):
        new = []
        for i in arg:
            if isinstance(i, str) and i.startswith('#'):
                new.append(self.var[int(i[1])])
            elif isinstance(i, list):
                nest = []
                for ii in i:
                    if isinstance(ii, str) and ii.startswith('#'):
                        nest.append(self.var[int(ii[1])])
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
        elif self.run_preposition(self.condition, condition):
            return True
        elif condition[0] == 'turn':
            condition[2] += 1
            if condition[2] >= condition[1]:
                condition[2] = 0
                return True
        elif condition[0] == 'be':
            return self.var
        elif condition[0] == 'bring':
            count = 0
            for i in self.var:
                if i != self:
                    if not condition[1] or condition[1] == i.name:
                        count += 1
            if count == condition[2]:
                return True
        elif condition[0] == 'reqvar':
            ok = False
            for i in self.var:
                from src.entity.unit.Character import Character
                if isinstance(i, Character):
                    if not i.require_var(condition[1], condition[2], cost=False):
                        return False
                    else:
                        ok = True
            return ok
        elif condition[0] == 'chance':
            if self.rand.rand_int(1, condition[1]) <= condition[2]:
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
            return Global.player.character.is_bright()
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
        elif condition[0] == 'wield':
            return Global.player.character.weapon.name in condition[1]

    def run_mechanism(self, arg):
        arg = self.replace_variable(arg)
        if self.run_preposition(self.mechanism, arg):
            pass
        elif arg[0] == 'exit':
            Global.player.control.quit()
        elif arg[0] == 'script':
            Script.execute_line(arg[1])
        elif arg[0] == 'trigger':
            for i in self.var:
                if isinstance(i, Scripter):
                    i.script.run()
        elif arg[0] == 'save':
            Data.write('raw/' + arg[1] + '.txt', arg[2])
        elif arg[0] == 'spawn':
            r = []
            from src.entity.Stock import Stock
            for i in arg[1]:
                r.append(Stock.make(i, self.var[0].pos))
            if len(arg) > 2:
                self.var[int(arg[2])] = r
        elif arg[0] == 'effect':
            Particle.make(arg[1], self.var[0].pos.get_center(), offset=8)
        elif arg[0] == 'toggle':
            Global.menu.toggle()
        elif arg[0] == 'message':
            Global.menu.get_message(arg[1])(None)
        elif arg[0] == 'dialog':
            Global.menu.topic(arg[1])
        elif arg[0] == 'say':
            from src.entity.unit.Character import Character
            for i in self.var:
                if isinstance(i, Character):
                    i.say(arg[1])
        elif arg[0] == 'settag':
            for i in self.var:
                i.tags[arg[1]] = arg[2]
        elif arg[0] == 'addtag':
            for i in self.var:
                i.tags[arg[1]] += arg[2]
        elif arg[0] == 'remove':
            for thing in reversed(self.var):
                thing.remove()
        elif arg[0] == 'hit':
            for thing in self.var:
                thing.hit(arg[2])
        elif arg[0] == 'buff':
            for thing in self.var:
                thing.states.add(arg[1], arg[2], var=arg[3])
        elif arg[0] == 'relocate':
            for thing in self.var:
                thing.relocate(arg[2], arg[3])
        elif arg[0] == 'move':
            for thing in self.var:
                thing.move(arg[2], arg[3])
        elif arg[0] == 'thief':
            from src.entity.unit.item.Item import Item
            for i in self.var[0].location.record:
                if isinstance(i, Item):
                    if i.get_value() >= arg[1]:
                        i.remove()
        elif arg[0] == 'sepia':
            Global.overlay.colorize([arg[1], arg[2], arg[3], arg[4]])
        elif arg[0] == 'blackout':
            Global.overlay.blackout()
        elif arg[0] == 'darkness':
            self.var[0].location.view_range = arg[1]
            self.var[0].location.sight_range = arg[2]
            self.var[0].location.resize()
        elif arg[0] == 'enter':
            from src.entity.Space import Space
            Global.player.travel(arg[1], Space(int(arg[2]), int(arg[3])))
        elif arg[0] == 'menu':
            Global.menu.var = self.var
            Global.menu.direct(getattr(Global.menu, 'menu_' + arg[1].lower()))
        elif arg[0] == 'load':
            building = Data.process_raw(Data.read('map/' + arg[1] + '.map'))
            flip = False
            if len(arg) > 2 and arg[2]:
                flip = True
            self.var[0].location.load_map(building, new=True, offset=self.where.to_list(), flip=flip)
        elif arg[0] == 'make':
            from src.map.Location import Location
            Location.make(arg[1], arg[2])
        elif arg[0] == 'makeif':
            from src.map.Location import Location
            Location.make(arg[1], arg[2], overwrite=False)
        elif arg[0] == 'give':
            from src.entity.unit.Character import Character
            from src.entity.Stock import Stock
            for gift in arg[1]:
                self.var[0].inventory.attempt_add(gift)
        elif arg[0] == 'unwield':
            Global.player.character.weapon.remove()
        elif arg[0] == 'act':
            from src.entity.unit.Unit import Unit
            for i in self.var:
                if isinstance(i, Unit):
                    i.action.set('wait')
                    i.form.set(arg[1])
                    i.delay = arg[2]
        elif arg[0] == 'sleep':
            Global.player.sleep(arg[1])
