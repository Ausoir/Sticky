import os
import ast
import pygame

cache = {}


def direct(fdir):
    return os.path.join('../Data/' + fdir)


def get_cache_image(fdir):
    if fdir not in cache:
        cache[fdir] = pygame.image.load(direct(fdir + '.png'))
    return cache[fdir]


def get_cache_file(fdir, ext):
    if fdir not in cache:
        cache[fdir] = read(fdir + '.' + ext)
    return cache[fdir]


def get_cache_clip(fdir):
    r = []
    clip = get_cache_file(fdir, '2d')
    lines = clip.split('\n\n')
    header = lines[0].split('\n')
    r.append(process_raw(header[0]))
    r.append(process_raw(header[1]))
    r.append(process_raw(lines[1]))
    r.append(process_raw(lines[2]))
    return r


def process_raw(data):
    r = ''
    data_flag = 0
    for x in data:
        if x not in ('[', ']', ',', '\n'):
            if data_flag == 0:
                r += '\''
                data_flag = 1
        else:
            if data_flag == 1:
                r += '\''
                data_flag = 0
        r += x
    return ast.literal_eval(",".join('['+x+']' for x in r.split('\n')))


def read(fdir):
    with open(direct(fdir), "U", newline='\n') as f:
        data = f.readlines()
        return '\n'.join([x.strip().split(' //')[0] for x in data])


def write(fdir, data):
    with open(direct(fdir), "U", newline='\n') as f:
        f.seek(0)
        f.write(data)
        f.truncate()

