class Test:
    def __init__(self, name, dur):
        self.name = name
        self.durability = dur


def aaa(damage):
    total = 0
    for i in items:
        if i.name == 'Studding' or i.name == 'Plating':
            final_damage = min(damage, i.durability)
            i.durability = i.durability - final_damage
            damage -= final_damage
            total += i.durability
    return total, damage


items = [Test('Plating', 0), Test('Studding', 0)]
print(aaa(1))
print(items)
