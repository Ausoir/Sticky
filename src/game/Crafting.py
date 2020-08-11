from src.tools.Data import Data
from src.tools.Dialog import Dialog


class Crafting:
    recipe = Data.process_raw(Data.read('data/raw/recipes.txt'))

    @staticmethod
    def get_ingredients(item):
        for i in Crafting.recipe:
            if i[0] == item:
                return i[1]

    @staticmethod
    def describe(item, resource=None):
        r = item
        r += '\n' + Dialog.get('ingredients') + ':'
        if not resource:
            resource = Crafting.get_ingredients(item)
        if resource:
            for i in resource:
                if i.startswith('#'):
                    i = Dialog.get('Any ') + i[1:].title()
                r += ' [' + i + ']'
        else:
            r += ' ' + Dialog.get('none')
        data = Data.get_line('descriptions.txt', item)
        if data:
            return r + '\n' + data[1]
        return r

    @staticmethod
    def is_craftable(host, resource):
        subjects = host.get_accessibles()
        materials = []
        for i in subjects:
            materials.append(i.name)
            materials.extend(i.tags.attributes.keys())
        for mat in resource:
            if mat.startswith('#'):
                mat = mat[1:]
            if mat not in materials:
                return False
        return True

    @staticmethod
    def craft(host, item, resource):
        resource = resource
        subjects = host.get_accessibles()
        for i in subjects:
            if i.name in resource:
                i.decay(1)
                resource.remove(i.name)
            for tag in i.tags.attributes.keys():
                if '#' + tag in resource:
                    i.decay(1)
                    resource.remove('#' + tag)
                    break
        from src.entity.Stock import Stock
        result = Stock.make(item, host.pos)
        if host.weapon:
            host.drop()
        result.on_wield(host)
        return result
