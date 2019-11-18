import os

import pyglet
from pyglet.image import TextureRegion

from src.form.Animation import Animation
from src.form.Picture import Picture


class Data:
    cache = {}
    registry_list = ['props', 'units', 'items', 'armors', 'weapons', 'headgears', 'spells', 'miscellaneous']

    @staticmethod
    def init():
        Data.set_cache('tiles', Data.process_raw(Data.get_cache_file('raw/tiles.txt')))
        for i in Data.registry_list:
            Data.set_cache(i, Data.process_raw(Data.get_cache_file('raw/' + i + '.txt')))
        res = Data.process_raw(Data.read('raw/resource.txt'))
        for i in res:
            image = Data.get_image(i[1], 0)
            Data.initialize_image(i[0], image, i[2])
        animation = Data.process_raw(Data.read('raw/animations.txt'))
        for i in animation:
            sequence = []
            for sprite in i[1]:
                sequence.append(Data.get_cache(sprite))
            Data.set_cache(i[0], [sequence, i[2], i[3]])

    @staticmethod
    def direct(fdir, path='../data/'):
        return os.path.join(path + fdir)

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
    def get_files(fdir, fn):
        return [m for m in os.listdir(Data.direct(fdir)) if fn(m)]

    @staticmethod
    def is_file(fdir):
        return os.path.exists(Data.direct(fdir))

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
    def get_form(fdir, **kwargs):
        cache = Data.get_cache(fdir)
        if cache:
            if isinstance(cache, TextureRegion):
                return Picture(cache, **kwargs)
            elif isinstance(cache, list):
                return Animation(cache, **kwargs)
            else:
                return cache
        else:
            return Picture(Data.get_image(fdir, False), **kwargs)

    @staticmethod
    def process_raw(data):
        lines = data.split('\n')
        if len(lines) > 1:
            return Data.parse(",".join('['+x+']' for x in data.split('\n')))
        return Data.parse(data)

    @staticmethod
    def parse(data):
        r = []
        raw = ''
        special = False
        while data:
            code = data[0]
            data = data[1:]
            if code == '\\':
                special = True
            elif special:
                raw += code
                special = False
            elif code == '[':
                data, result = Data.parse(data)
                r.append(result)
            elif code == ']':
                if raw:
                    if raw.isdigit() or raw[0] == '-':
                        raw = int(raw)
                    r.append(raw)
                return data, r
            elif code == ',':
                if raw:
                    if raw.isdigit() or raw[0] == '-':
                        raw = int(raw)
                    r.append(raw)
                    raw = ''
            else:
                raw += code
        if raw:
            if raw.isdigit() or raw[0] == '-':
                raw = int(raw)
            r.append(raw)
        return r

    @staticmethod
    def get_line(fdir, name):
        data = Data.process_raw(Data.read(fdir))
        for i in data:
            if i[0] == name:
                return i

    @staticmethod
    def initialize_image(name, texture, subset_size):
        cols = int(texture.width / subset_size[0])
        rows = int(texture.height / subset_size[1])
        for x in range(0, cols+1):
            for y in range(0, rows+1):
                left = subset_size[0] * x
                bottom = texture.height - subset_size[1] * (y + 1)
                region = texture.get_region(left, bottom, subset_size[0], subset_size[1])
                Data.cache[name+'_'+str(x)+'x'+str(y)] = region

    @staticmethod
    def get_image(fdir, cache):
        if cache:
            Data.cache[fdir] = Picture(pyglet.resource.image(Data.direct(fdir + '.png', path='')))
            return Data.cache[fdir]
        else:
            return pyglet.resource.image(Data.direct(fdir + '.png', path=''))

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
            clip = Data.read(fdir + '.2d')
            lines = clip.split('\n\n')
            r.append(Data.process_raw(lines[0]))
            r.append(Data.process_raw(lines[1]))
            r.append(Data.process_raw(lines[2]))
            Data.set_cache(fdir, r)
            return r
        return cache
