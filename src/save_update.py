import os

from src.tools.Data import Data

directory = '../data/map'
output_directory = '../data/map'
count = 0
for d in os.listdir(Data.direct(directory)):
    if d.startswith('x'):
        count += 1
        data = Data.read(directory + '/' + d).split('\n')
        data[0] = '0,-12'
        Data.write(output_directory + '/' + d, '\n'.join(data))
        print('updating ' + d)
print('process updated ' + str(count) + ' files')
