from src.entity.Stock import Stock, Dialog
from src.game import Global


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
        if host.weapon and host.weapon.name == 'Bottle':
            host.drop().remove()
            water = Stock.make('Water Bottle', host.pos)
            Global.main.monologue.set(Dialog.get('obtain', [water.name]))
            if host.inventory.is_vacant(water.get_weight()):
                water.on_wield(host)

    @staticmethod
    def push(host, var):
        def fn():
            front = var.pos.get_cardinal(var.direction, 1)
            if host in front.things:
                var.action.side_step(front)
        if var.action.delay == 0:
            var.face_toward(host.pos)
            var.action.act('interact', 8)
            var.action.on_finish = fn
