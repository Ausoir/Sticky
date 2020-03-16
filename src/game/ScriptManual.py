from src.game import Global


class ScriptManual:
    @staticmethod
    def execute(arg, host=None, var=None):
        getattr(ScriptManual, arg)(arg, host, var)

    @staticmethod
    def search(name, host, var):
        def confirm(index):
            from src.entity.Stock import Stock
            Stock.make(item, var.pos)
            host.tags.remove('loot')
            Global.menu.toggle()
        item = host.get_loot()
        if item:
            from src.tools.Dialog import Dialog
            Global.menu.get_prompt(Dialog.get('pickup', [item]), Dialog.get('proceed'), confirm)(None)
        var.action.act('grab', 8)

    @staticmethod
    def rspawn(name, host, var):
        from src.entity.Stock import Stock
        Stock.make(Global.r.rand_list([v for v in Stock.registry.values()])[0], host.pos)
        host.action.act('grab', 8)
