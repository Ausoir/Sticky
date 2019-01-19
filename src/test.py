from src.form.GroupSprite import GroupSprite

class ASD:
    def __init__(self, d):
        self.depth = d

test = GroupSprite()
test.add(ASD(4))
test.add(ASD(3))
test.add(ASD(1))
test.add(ASD(2))
print(test)