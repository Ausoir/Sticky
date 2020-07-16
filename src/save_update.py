import os

from src.tools.Data import Data

directory = '../data/map'
for d in os.listdir(Data.direct(directory)):
    if d.startswith('x'):
        data = Data.read(directory + '/' + d).split('\n')
        data[0] = '0,0'
        Data.write(directory + '/' + d, '\n'.join(data))
