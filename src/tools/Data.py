import ast
import os

import pygame


class Data:
    cache = {}
    registry_list = ['props', 'units', 'items', 'armors', 'weapons', 'headgears', 'projectiles']

    @staticmethod
    def init():
        for i in Data.registry_list:
            Data.set_cache(i, Data.process_raw(Data.get_cache_file('data/raw/' + i + '.txt')))
        res = Data.process_raw(Data.read('data/resource.txt'))
        for x in res:
            Data.initialize_image(x[0], x[1], x[2])

    @staticmethod
    def direct(fdir):
        return os.path.join('../' + fdir)

    @staticmethod
    def read(fdir):
        with open(Data.direct(fdir), "U", newline='\n') as f:
            data = f.readlines()
            return '\n'.join([x.strip().split(' //')[0] for x in data])

    @staticmethod
    def write(fdir, data):
        with open(Data.direct(fdir), "w", newline='\n') as f:
            f.seek(0)
            f.write(data)
            f.truncate()

    @staticmethod
    def get_cache(fdir):
        if fdir not in Data.cache:
            return None
        return Data.cache[fdir]

    @staticmethod
    def set_cache(fdir, arg):
        if fdir not in Data.cache:
            Data.cache[fdir] = arg

    @staticmethod
    def process_raw(data):
        r = ''
        data_flag = 0
        for x in data:
            if x != '-':
                if x not in ('[', ']', ',', '\n'):
                    if data_flag == 0:
                        if x.isdigit():
                            data_flag = 2
                        else:
                            r += '\''
                            data_flag = 1
                else:
                    if data_flag == 1:
                        r += '\''
                        data_flag = 0
                    elif data_flag == 2:
                        data_flag = 0
            r += x
        if data_flag == 1:
            r += '\''
        return ast.literal_eval(",".join('['+x+']' for x in r.split('\n')))

    @staticmethod
    def initialize_image(name, fdir, subset_size):
        image = Data.get_image(fdir, 0)
        size = image.get_size()
        if subset_size == 0:
            surface = pygame.Surface((size[0], size[1]), pygame.SRCALPHA, 32)
            surface.blit(image, (0, 0))
            Data.cache[name] = surface
        else:
            cols = int(size[0] / subset_size[0])
            rows = int(size[1] / subset_size[1])
            for x in range(0, cols+1):
                for y in range(0, rows+1):
                    surface = pygame.Surface((subset_size[0], subset_size[1]), pygame.SRCALPHA, 32)
                    surface.blit(image, (0, 0), (subset_size[0]*x, subset_size[1]*y, subset_size[0], subset_size[1]))
                    Data.cache[name+'_'+str(x)+'x'+str(y)] = surface

    @staticmethod
    def get_image(fdir, cache):
        if cache:
            if fdir not in Data.cache:
                Data.cache[fdir] = pygame.image.load(Data.direct(fdir + '.png'))
            return Data.cache[fdir]
        else:
            return pygame.image.load(Data.direct(fdir + '.png'))

    @staticmethod
    def get_cache_file(fdir):
        cache = Data.get_cache(fdir)
        if not cache:
            r = Data.read(fdir)
            Data.set_cache(fdir, r)
            return r
        return cache

    @staticmethod
    def get_cache_clip(fdir):
        cache = Data.get_cache(fdir)
        if not cache:
            r = []
            clip = Data.read('data/' + fdir + '.2d')
            lines = clip.split('\n\n')
            r.append(Data.process_raw(lines[0]))
            r.append(Data.process_raw(lines[1]))
            r.append(Data.process_raw(lines[2]))
            Data.set_cache(fdir, r)
            return r
        return cache

    @staticmethod
    def get_cache_processed(fdir):
        cache = Data.get_cache(fdir)
        if not cache:
            r = Data.process_raw(Data.read(fdir))
            Data.set_cache(fdir, r)
            return r
        return cache
