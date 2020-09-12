import math

from src.game import Global
from src.tools.Dialog import Dialog


class ScriptManual:
    @staticmethod
    def execute(arg, host=None, var=None):
        getattr(ScriptManual, arg)(host, var)

    @staticmethod
    def swap(host, var):
        def fn():
            front = var.pos.get_cardinal(var.direction)
            from src.entity.unit.Unit import Unit
            for i in front.things:
                if isinstance(i, Unit) and i.tags.get('team') == var.tags.get('team'):
                    old = i.pos
                    i.relocate(to=var.pos)
                    var.action.move(old)
        if var.action.delay == 0:
            var.action.act('interact', 1)
            var.action.on_finish = fn

    @staticmethod
    def ally(host, var):
        if host != Global.player.character or Global.player.is_sociable(1):
            var.tags.set('summon', 1)
            var.tags.set('team', host.tags.get('team', 0))
            Global.world.location.population.adjust(var)
            pos = host.pos - var.pos
            var.tags.set('tgt', 'x' + str(pos.x) + 'y' + str(pos.y))
            var.pilot.load('ally')
            var.tags.set('#', '>menu>order')
            if host == Global.player.character:
                Global.main.monologue.set(Dialog.get(':join', [var.get_display_name()]))

    @staticmethod
    def companion(host, var):
        front = host.pos.get_cardinal(host.direction)
        if host.tags.get('summon', 0) == 0:
            for thing in front.things:
                if thing.tags.get('summon', 0) == 1 and thing.tags.get('p', 0) > 0:
                    Global.player.companions.append(thing.__str__())
                    Global.main.monologue.set(Dialog.get(':companion', [thing.get_display_name()]))
                    thing.remove()
                    return
        if Global.player.companions:
            from src.tools.Data import Data
            from src.entity.Stock import Stock
            data = Data.process_raw(Global.player.companions.pop())
            unit = Stock.get(data[1], data)
            unit.pos = front
            unit.add()
            if unit.tags.get('#', '') == 'reclaim':
                unit.tags.remove('#')
                Global.player.set_player(unit)

    @staticmethod
    def uncontrol(host, var):
        if var.tags.get('summon', 0) == 1 and Global.player.companions:
            from src.tools.Data import Data
            from src.entity.Stock import Stock
            data = Data.process_raw(Global.player.companions.pop())
            unit = Stock.get(data[1], data)
            unit.pos = var.pos
            unit.add()
            Global.player.set_player(unit)

    @staticmethod
    def repair(host, var):
        for item in host.get_accessibles():
            if item.tags.get('iron', 0) == 1:
                from src.entity.unit.Humanoid import Humanoid
                if isinstance(host, Humanoid):
                    for i in [host.armor, host.headgear, host.weapon]:
                        if i:
                            mhp = i.tags.get('P')
                            if mhp:
                                i.tags.set('p', mhp)
                Global.main.monologue.set(Dialog.get(':repair'))
                item.remove()
                return
        Global.main.monologue.set(Dialog.get(':req_item', ['Iron']))

    @staticmethod
    def alchemy(host, var):
        if host.get_skill('alchemy'):
            if host.weapon and host.weapon.tags.get('alchemy'):
                Global.world.location.sound.register(host.pos, 0, file='mix')
                seed = host.weapon.tags.get('seed')
                density = seed % 100
                acidity = density - (abs(math.sin(seed % 101)) * density)
                toxicity = density - (abs(math.sin(seed % 102)) * density)
                var.tags.increment('density', int(density))
                var.tags.increment('acidity', int(acidity))
                var.tags.increment('toxicity', int(toxicity))
                host.drop().remove()
            elif host.weapon and var.tags.get('density') and host.weapon.tags.get('container'):
                Global.world.location.sound.register(host.pos, 0, file='drain')
                host.drop().remove()
                from src.entity.Stock import Stock
                potion = Stock.make('Potion', host.pos)
                density = var.tags.get('density', 0)
                acidity = var.tags.get('acidity', 0)
                toxicity = var.tags.get('toxicity', 0)
                from src.tools.Data import Data
                data = Data.get_line('raw.txt', 'potions')[1]
                effect_num = len(data) - 1
                if acidity < toxicity:
                    effect = acidity / toxicity
                else:
                    effect = toxicity / acidity
                effect = int(effect * effect_num)
                potion.tags.set('effect', data[effect][0])
                potion.tags.set('dur', int(data[effect][1] * min(100, density) * .1 + 1))
                potion.tags.set('var', data[effect][2])
                var.tags.increment('density', int(-density))
                if host.is_vacant(potion.get_weight()):
                    potion.on_wield(host)
                var.tags.remove('density')
                var.tags.remove('acidity')
                var.tags.remove('toxicity')
            else:
                require = []
                ingredient = var.tags.get('density')
                if ingredient:
                    require.append('<' + Dialog.get('Container') + '>')
                else:
                    require.append('<' + Dialog.get('Ingredients') + '>')
                Global.menu.get_message(Dialog.get(':req_item', [','.join(require)]))()
        else:
            Global.main.monologue.set(Dialog.get(':req_skill', [Dialog.get('Alchemy')]))

    @staticmethod
    def carve(host, var):
        if host.get_skill('carving'):
            if host.weapon:
                if host.weapon.tags.get('wood') == 1:
                    Global.world.location.sound.register(host.pos, 0, file='mix')
                    host.drop().remove()
                    var.tags.set('stick', 1)
                elif host.weapon.tags.get('jewel'):
                    Global.world.location.sound.register(host.pos, 0, file='mix')
                    var.tags.set('jewel', host.weapon.tags.get('jewel'))
                    var.tags.set('jewelt', host.weapon.tags.get('jewelt'))
                    host.drop().remove()
                else:
                    spell = host.weapon.tags.get('spell')
                    if spell:
                        host.drop().remove()
                        Global.world.location.sound.register(host.pos, 0, file='mix')
                        var.tags.set('spell', spell)
                if var.tags.get('stick') and var.tags.get('jewel') and var.tags.get('spell'):
                    var.tags.remove('stick')
                    jewel = var.tags.remove('jewel')
                    jewelt = var.tags.remove('jewelt')
                    spell = var.tags.remove('spell')
                    from src.entity.Stock import Stock
                    wand = Stock.make(jewelt.title(), host.pos)
                    wand.tags.set('P', jewel)
                    wand.tags.set('p', jewel)
                    wand.tags.set('spell', spell)
                    if host.is_vacant(wand.get_weight()):
                        wand.on_wield(host)
            else:
                require = []
                if not var.tags.get('stick'):
                    require.append('<' + Dialog.get('Wood') + '>')
                if not var.tags.get('jewel'):
                    require.append('<' + Dialog.get('Jewel') + '>')
                if not var.tags.get('spell'):
                    require.append('<' + Dialog.get('Spell') + '>')
                Global.menu.get_message(Dialog.get(':req_item', [','.join(require)]))()
        else:
            Global.main.monologue.set(Dialog.get(':req_skill', [Dialog.get('Carving')]))

    @staticmethod
    def draw(host, var):
        if host.get_skill('conjuration'):
            from src.entity.Stock import Stock
            marker = Stock.make('Marker', host.pos)
            marker.tags.set('seed', var.get_seed())
            marker.trigger()
        else:
            Global.main.monologue.set(Dialog.get(':req_skill', [Dialog.get('Conjuration')]))

    @staticmethod
    def shapeshift(host, var, data=None):
        from src.entity.unit.Unit import Unit
        if not host.tags.get('silver') and isinstance(host, Unit):
            old_host = host
            from src.entity.Stock import Stock
            if data:
                unit = Stock.get(var, data=data)
                unit.add()
            else:
                unit = Stock.make(var, host.pos)
                old_host.states.set_host(unit)
            if old_host == Global.player.character:
                unit.tags.remove('ai')
            unit.face(old_host.direction)
            old_host.remove()
            if old_host == Global.player.character:
                Global.player.set_player(unit)
            Global.world.location.sound.register(host.pos, 8, file='void')
            return unit
        else:
            from src.entity.Particle import Particle
            Particle.make('sonic', host.pos)

    @staticmethod
    def observe(host, var):
        scholar = host.tags.get('class', 'classless') == 'scholar'
        wait = Global.player.days - host.tags.get('observe', -12)
        if scholar:
            wait -= 6
        else:
            wait -= 12
        if wait >= 0:
            front = host.pos.get_cardinal(host.direction)
            for i in front.things:
                from src.entity.unit.Unit import Unit
                if isinstance(i, Unit) and i.name != host.tags.get('observed', ''):
                    host.tags.set('observe', Global.player.days)
                    host.tags.set('observed', i.name)
                    exp = i.get_level()
                    unit_team = i.tags.get('team', 0)
                    if unit_team != host.tags.get('team', 0):
                        exp *= 2
                    Global.menu.get_message(i.describe() + '\n' + Dialog.get(':observe', [max(0, exp)]))(0)
                    host.progress_level(exp, mode='observe')
                    if not scholar:
                        var.decay(1)
                    return
        else:
            Global.main.monologue.set(Dialog.get('!observe', [-wait]))

    @staticmethod
    def reclaim(host, var):
        x = host.tags.get('tox')
        y = host.tags.get('toy')
        Global.world.travel(x, y)
        candidates = []
        from src.entity.unit.Unit import Unit
        for i in Global.world.location.population.get_units():
            if i != host and isinstance(i, Unit) and i.tags.get('husk'):
                candidates.append(i)
        closest = None
        for i in candidates:
            diff = (i.pos - host.pos).difference()
            if not closest or diff < (closest - host.pos).difference():
                closest = i.pos
        if closest:
            for i in closest.things:
                if i != host and isinstance(i, Unit) and i.tags.remove('husk'):
                    host.remove()
                    Global.player.set_player(i)
                    break
            Global.player.sleep(0)

    @staticmethod
    def raid(host, var):
        direction = Global.r.rand_int(0, 3)
        from src.tools.Data import Data
        for i in range(20):
            enemy = Global.r.rand_list(Data.get_line('habitat.txt', var)[1])
            if enemy:
                host_pos = Global.player.character.pos
                distance = 9
                if direction == 0:
                    from_x = host_pos.x - distance - Global.r.rand_int(0, 3)
                    from_y = host_pos.y + Global.r.rand_int(-distance, distance)
                elif direction == 1:
                    from_x = host_pos.x + Global.r.rand_int(-distance, distance)
                    from_y = host_pos.y - distance - Global.r.rand_int(0, 3)
                elif direction == 2:
                    from_x = host_pos.x + distance + Global.r.rand_int(0, 3)
                    from_y = host_pos.y + Global.r.rand_int(-distance, distance)
                else:
                    from_x = host_pos.x + Global.r.rand_int(-distance, distance)
                    from_y = host_pos.y + distance + Global.r.rand_int(0, 3)
                tile = Global.world.location.get_tile(from_x, from_y)
                if tile and tile.get_solidity() == 0:
                    from src.entity.Stock import Stock
                    enemy = Stock.make(enemy, tile)
                    enemy.pilot.set_task(enemy.pilot.attack)
                    enemy.pilot.task.target = Global.player.character
