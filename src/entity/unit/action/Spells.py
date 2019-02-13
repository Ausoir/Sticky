from src.entity.Stock import Stock
from src.form.Effect import Effect
from src.tools.Random import Random


class Spells:
    @staticmethod
    def charm(host):
        if host.states.get('air') and 'levitate' in host.action.spells:
            host.states.add('levitate', 60)
        elif host.states.get('fire') and 'brand' in host.action.spells:
            host.states.add('fire', 120)
            host.weapon.states.add('fire', 120)
        else:
            Spells.scry(host)

    @staticmethod
    def cast(host):
        if host.states.get('fire') and 'fireblast' in host.action.spells:
            Spells.fireblast(host)
        else:
            Spells.blast(host)

    @staticmethod
    def scry(host):
        def effect():
            r.fly(host.next_target.x, host.next_target.y, 2, flag=[])
            if r.count <= 1:
                host.center_camera()
        r = Stock.get('Force', host.location).add_to(host.faction, host.pos[0])
        host.states.add('stun', 40)
        r.count = 40
        r.center_camera()
        r.effect = effect

    @staticmethod
    def blast(host):
        host.location.attack.register(1, host.get_target_tile(), 1, type='zip')
        Effect.energy(host.get_target_tile().get_center())

    @staticmethod
    def ignite(host):
        if host.states.get('fire'):
            host.states.add('insulation', 120)
        else:
            host.states.add('fire', 30)
            host.weapon.states.add('fire', 30)

    @staticmethod
    def whirlwind(host):
        host.states.add('air', 8)

    @staticmethod
    def conjure(host):
        Effect.barrier(host.pos[0].get_center()).pos = host.motion_pos
        r = Stock.get('Crate', host.location).add()
        r.relocate(host.pos[0].x, host.pos[0].y)
        host.states.add('rift', 240, var=r.id)

    @staticmethod
    def burn(target):
        target.states.add('burn', 4)

    @staticmethod
    def fireblast(host):
        def effect():
            r.fly(final_dir, Random.rand_int(-1, 2), 1)
            r.location.attack.register(1, r.pos[0], 1, type=0, callback=Spells.burn)
            Effect.explode(r.pos[0].get_center(), final_dir)
        r = Stock.get('Force', host.location).add_to(host.faction, host.get_offset_tile(host.direction, 0))
        r.durability = 10
        r.count = 10
        final_dir = host.direction
        r.effect = effect

    @staticmethod
    def rift(host):
        def effect():
            r.launch(r.pos[0].x, r.pos[0].y, host.next_target.x, host.next_target.y, distance=1)
            Effect.wind(r.pos[0].get_center())
        r = Stock.get('Force', host.location).add()
        r.count = -1
        r.launch(host.pos[0].x, host.pos[0].y, host.next_target.x, host.next_target.y)
        r.center_camera()
        r.effect = effect
        host.states.add('scry', 140, var=r.id)
