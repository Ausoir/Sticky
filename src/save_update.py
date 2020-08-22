import os

from src.tools.Data import Data

input_directory = '../save'
# input_directory = '../data/map'
output_directory = '../data/map'
count = 0
for d in os.listdir(Data.direct(input_directory)):
    if d.startswith('x'):
        count += 1
        data = Data.read(input_directory + '/' + d).split('\n')
        if data[0] != '-24':
            print('updating ' + d)
        if data[1] == '':
            if data[2].replace('~', '').replace('%', '') == '':
                print('deleting ' + d)
                Data.delete(output_directory + '/' + d)
                continue
        data[0] = '-24'
        Data.write(output_directory + '/' + d, '\n'.join(data))
print('process updated ' + str(count) + ' files')
