from src.game import Global


class ScriptManual:
    @staticmethod
    def execute(arg, host=None):
        getattr(ScriptManual, arg)(arg, host)

    @staticmethod
    def rspawn(name, host):
        from src.entity.Stock import Stock
        Stock.make(Global.r.rand_list([v for v in Stock.registry.values()])[0], host.pos)
        host.action.act('grab', 8)

    @staticmethod
    def fire(name, host):
        host.states.add('Burn', 16)
