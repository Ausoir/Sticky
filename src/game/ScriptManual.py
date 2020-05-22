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
    def water(host, var):
        if host.weapon and host.weapon.tags.get('water') == 0:
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
            if host.weapon:
                water = host.weapon.tags.get('water', -1)
                table_water = var.tags.get('water', 0)
                if water > 0:
                    host.location.sound.register(host.pos, 0, file='drain')
                    host.face_toward(var.pos)
                    host.action.act('interact', 8)
                    Global.main.monologue.set(Dialog.get('water_fill'))
                    host.weapon.switch_form()
                    host.weapon.tags.set('water', 0)
                    var.tags.increment('water', 1)
                elif host.weapon.tags.get('alchemy'):
                    host.location.sound.register(host.pos, 0, file='mix')
                    seed = host.weapon.tags.get('seed')
                    density = seed % 100
                    acidity = density - (abs(math.sin(seed % 101)) * density)
                    toxicity = density - (abs(math.sin(seed % 102)) * density)
                    var.tags.increment('density', int(density))
                    var.tags.increment('acidity', int(acidity))
                    var.tags.increment('toxicity', int(toxicity))
                    host.drop().remove()
                elif water == 0 and table_water > 0:
                    host.location.sound.register(host.pos, 0, file='drain')
                    host.drop().remove()
                    from src.entity.Stock import Stock
                    potion = Stock.make('Potion', host.pos)
                    density = var.tags.get('density', 0) / table_water  # how effective potion is
                    acidity = var.tags.get('acidity', 0) / table_water  # how long before expiry
                    toxicity = var.tags.get('toxicity', 0) / table_water  # side effects
                    potion.tags.set('density', int(density))
                    potion.tags.set('acidity', int(acidity))
                    potion.tags.set('toxicity', int(toxicity))
                    var.tags.increment('density', int(-density))
                    if host.inventory.is_vacant(potion.get_weight()):
                        potion.on_wield(host)
                    if table_water == 1:
                        var.tags.remove('density')
                        var.tags.remove('acidity')
                        var.tags.remove('toxicity')
                    var.tags.increment('water', -1)
        else:
            Global.main.monologue.set(Dialog.get('req_skill', [Dialog.get('Alchemy')]))

    @staticmethod
    def draw(host, var):
        if host.get_skill('conjuration'):
            from src.entity.Stock import Stock
            marker = Stock.make('Marker', host.pos)
            marker.tags.set('seed', var.tags.get('seed', 0))
            marker.trigger()
        else:
            Global.main.monologue.set(Dialog.get('req_skill', [Dialog.get('Conjuration')]))
