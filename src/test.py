from src.other import Data

data = Data.read('raw/Loot.txt')

r = Data.process_raw(data)[1]

print(r)
