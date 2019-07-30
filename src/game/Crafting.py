from src.game.Tags import Tags
from src.tools.Data import Data


class Crafting:
    recipe = Data.process_raw(Data.get_cache_file('data/raw/recipes.txt'))

    @staticmethod
    def get_ingredients(item):
        for i in Crafting.recipe:
            if i[0] == item:
                return i[1]

    @staticmethod
    def describe(item):
        res = Crafting.get_ingredients(item)
        r = item
        r += '\nIngredients:'
        if res:
            for i in res:
                if i.startswith('#'):
                    i = 'Any ' + Tags.name(i[1:]).title()
                r += ' [' + i + ']'
        else:
            r += ' None'
        for i in Crafting.recipe:
            if i[0] == item:
                from src.entity.unit.item.Item import Item
                if item in Item.description:
                    return r + '\n' + Item.description[item]
                return r

    @staticmethod
    def is_craftable(host, item):
        subjects = host.get_accessibles()
        materials = []
        for i in subjects:
            materials.append(i.name)
            materials.extend(i.tags)
        resource = Crafting.get_ingredients(item)
        for mat in resource:
            if mat.startswith('#'):
                mat = mat[1:]
            if mat not in materials:
                return False
        return True

    @staticmethod
    def craft(host, item):
        resource = Crafting.get_ingredients(item)
        subjects = host.get_accessibles()
        for i in subjects:
            if i.name in resource:
                i.hit(1)
                resource.remove(i.name)
            for tag in i.tags:
                if '#' + tag in resource:
                    i.hit(1)
                    resource.remove('#' + tag)
                    break
        from src.entity.Stock import Stock
        result = Stock.make(item, host.pos[0])
        if host.is_armed():
            host.drop()
        result.on_equip(host)
        return result
