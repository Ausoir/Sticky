import math

from src.game import Global
from src.tools.Dialog import Dialog


class ScriptManual:
    @staticmethod
    def execute(arg, host=None, var=None):
        getattr(ScriptManual, arg)(host, var)

    @staticmethod
    def search(host, var):
        def confirm(index):
            from src.entity.Stock import Stock
            Stock.make(item, host.pos)
            var.tags.remove('loot')
        item = var.get_loot()
        if item:
            Global.menu.get_prompt(Dialog.get('pickup', [item]), Dialog.get('proceed'), confirm)(None)
        host.action.act('grab', 8)

    @staticmethod
    def replenish(host, var):
        def confirm(index):
            from src.entity.Stock import Stock
            Stock.make(item, host.pos)
        item = var.get_loot()
        if item:
            Global.menu.get_prompt(Dialog.get('pickup', [item]), Dialog.get('proceed'), confirm)(None)
        host.action.act('grab', 8)

    @staticmethod
    def water(host, var):
        from src.entity.unit.Humanoid import Humanoid
        if isinstance(host, Humanoid) and host.weapon and host.weapon.tags.get('water') == 0:
            host.location.sound.register(host.pos, 0, file='drain')
            host.weapon.switch_form()
            host.weapon.tags.set('water', 1)
            Global.main.monologue.set(Dialog.get('water_fill'))

    @staticmethod
    def push(host, var):
        def fn():
            front = var.pos.get_cardinal(var.direction, 1)
            if host in front.things:
                old = host.pos
                host.relocate(to=var.pos)
                var.action.move(old)
        if var.action.delay == 0:
            var.face_toward(host.pos)
            var.action.act('interact', 4)
            var.action.on_finish = fn

    @staticmethod
    def alchemy(host, var):
        if host.get_skill('alchemy'):
            if host.weapon and host.weapon.tags.get('alchemy'):
                host.location.sound.register(host.pos, 0, file='mix')
                seed = host.weapon.tags.get('seed')
                density = seed % 100
                acidity = density - (abs(math.sin(seed % 101)) * density)
                toxicity = density - (abs(math.sin(seed % 102)) * density)
                var.tags.increment('density', int(density))
                var.tags.increment('acidity', int(acidity))
                var.tags.increment('toxicity', int(toxicity))
                host.drop().remove()
            elif host.weapon and var.tags.get('density') and host.weapon.tags.get('container'):
                host.location.sound.register(host.pos, 0, file='drain')
                host.drop().remove()
                from src.entity.Stock import Stock
                potion = Stock.make('Potion', host.pos)
                density = var.tags.get('density', 0)
                acidity = var.tags.get('acidity', 0)
                toxicity = var.tags.get('toxicity', 0)
                if density >= 50:
                    from src.tools.Data import Data
                    data = Data.get_line('raw.txt', 'potions')[1]
                    effect_num = len(data) - 1
                    if acidity < toxicity:
                        effect = acidity / toxicity
                    else:
                        effect = toxicity / acidity
                    effect = int(effect * effect_num)
                    potion.tags.set('effect', data[effect][0])
                    potion.tags.set('dur', int(data[effect][1] * min(100, density - 50) * .1 + 1))
                    potion.tags.set('var', data[effect][2])
                    potion.tags.set('time', Global.player.days + density)
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
                Global.menu.get_message(Dialog.get('req_item', [','.join(require)]))()
        else:
            Global.menu.get_message(Dialog.get('req_skill', [Dialog.get('Alchemy')]))()

    @staticmethod
    def carve(host, var):
        if host.get_skill('carving'):
            if host.weapon:
                if host.weapon.tags.get('wood') == 1:
                    host.location.sound.register(host.pos, 0, file='mix')
                    host.drop().remove()
                    var.tags.set('stick', 1)
                elif host.weapon.tags.get('jewel'):
                    host.location.sound.register(host.pos, 0, file='mix')
                    jewel = host.weapon.tags.get('jewel')
                    host.drop().remove()
                    var.tags.set('jewel', jewel)
                else:
                    spell = host.weapon.tags.get('spell')
                    if spell:
                        power = host.weapon.tags.get('power', 0)
                        host.drop().remove()
                        host.location.sound.register(host.pos, 0, file='mix')
                        var.tags.set('spell', spell)
                        var.tags.set('power', power)
                if var.tags.get('stick') and var.tags.get('jewel') and var.tags.get('spell'):
                    var.tags.remove('stick')
                    jewel = var.tags.remove('jewel')
                    spell = var.tags.remove('spell')
                    power = var.tags.remove('power')
                    from src.entity.Stock import Stock
                    wand = Stock.make('Wand', host.pos)
                    wand.tags.set('P', jewel)
                    wand.tags.set('p', jewel)
                    wand.tags.set('spell', spell)
                    wand.tags.set('power', power)
                    if host.is_vacant(wand.get_weight()):
                        wand.on_wield(host)
            else:
                require = []
                if not var.tags.get('stick'):
                    require.append('<' + Dialog.get('Stick') + '>')
                if not var.tags.get('jewel'):
                    require.append('<' + Dialog.get('Jewel') + '>')
                if not var.tags.get('spell'):
                    require.append('<' + Dialog.get('Potion') + '>')
                Global.menu.get_message(Dialog.get('req_item', [','.join(require)]))()
        else:
            Global.menu.get_message(Dialog.get('req_skill', [Dialog.get('Carving')]))()

    @staticmethod
    def draw(host, var):
        if host.get_skill('conjuration'):
            from src.entity.Stock import Stock
            marker = Stock.make('Marker', host.pos)
            marker.tags.set('seed', var.get_seed())
            marker.trigger()
        else:
            Global.menu.get_message(Dialog.get('req_skill', [Dialog.get('Conjuration')]))()

    @staticmethod
    def shapeshift(host, var, data=None):
        if not host.tags.get('silver'):
            from src.entity.Stock import Stock
            if data:
                unit = Stock.get(host.location, var, data=data)
                unit.add()
            else:
                unit = Stock.make(var, host.pos)
            unit.tags.remove('ai')
            old_host = host
            for i in host.states.buffs:
                i.host = unit
            unit.states = old_host.states
            unit.skills = old_host.skills
            unit.face(old_host.direction)
            from src.entity.unit.Buffs import Buffs
            old_host.states = Buffs(old_host)
            old_host.remove()
            if old_host == Global.player.character:
                Global.player.set_player(unit)
            host.location.sound.register(host.pos, 8, file='void')
            return unit
        else:
            from src.entity.Particle import Particle
            Particle.make('sonic', host.pos)
