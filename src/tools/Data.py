import os

import pyglet
from pyglet.image import Texture, Animation

from src.form.Model import Model
from src.form.Picture import Picture
from src.game import Global


class Data:
    cache = {}
    registry_list = ['props', 'units', 'items', 'armors', 'weapons', 'headgears', 'spells', 'miscellaneous']

    @staticmethod
    def init():
        Data.set_cache('none', Texture.create(1, 1))
        Data.set_cache('tiles', Data.process_raw(Data.read('raw/tiles.txt')))
        for i in Data.registry_list:
            Data.set_cache(i, Data.process_raw(Data.read('raw/' + i + '.txt')))
        res = Data.process_raw(Data.read('raw/resource.txt'))
        for i in res:
            Data.initialize_image(i[0], i[1], i[2])
        animation = Data.process_raw(Data.read('raw/animations.txt'))
        for i in animation:
            sequence = []
            for sprite in i[1]:
                sequence.append(Data.get_cache(sprite))
            loop = bool(i[3])
            if not loop:
                sequence.append(Data.get_cache('none'))
            ani = pyglet.image.Animation.from_image_sequence(sequence, period=float(i[2]), loop=loop)
            Data.set_cache(i[0], ani)

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
    def get_form(fdir, form=None, **kwargs):
        cache = Data.get_cache(fdir)
        if not cache:
            cache = Data.get_image(fdir, False)
        if not form:
            if cache:
                if isinstance(cache, Texture) or isinstance(cache, Animation):
                    return Picture(cache, **kwargs)
                else:
                    return cache
        else:
            if form.startswith('Unit'):
                div = int(form[4:])
                width = int(cache.width / div)
                height = int(cache.height / 3)
                return Data.get_model(cache, width, height, **kwargs)
            elif form == 'Head':
                height = int(cache.height / 3)
                return Data.get_model(cache, cache.width, height, **kwargs)
            elif form == 'Humanoid':
                return Data.get_model(cache, 16, 32, **kwargs)

    @staticmethod
    def get_model(image, width, height, **kwargs):
        if width == 0 or height == 0:
            return Global.blank_form
        cols = int(image.width / width)
        rows = int(image.height / height)
        if cols == 0 or rows == 0:
            return Global.blank_form
        region = []
        for y in range(0, rows):
            for x in range(0, cols):
                left = width * x
                bottom = image.height - height * (y + 1)
                region.append(image.get_region(left, bottom, width, height))
        return Model(region, **kwargs)

    @staticmethod
    def initialize_image(name, texture, subset_size):
        # explosion = pyglet.image.load(Data.direct(texture + '.png', path='../data/'))
        # explosion_seq = pyglet.image.ImageGrid(explosion, subset_size[1], subset_size[0])
        # seq = pyglet.image.Texture3D.create_for_image_grid(explosion_seq)
        # i = 0
        # for y in range(subset_size[1]):
        #     for x in range(subset_size[0]):
        #         Data.cache[name + '_' + str(x) + 'x' + str(subset_size[1] - y - 1)] = seq[i]
        #         i += 1
        texture = Data.get_image(texture, False)
        width = int(texture.width / subset_size[0])
        height = int(texture.height / subset_size[1])
        for x in range(subset_size[0]):
            for y in range(subset_size[1]):
                left = width * x
                bottom = texture.height - height * (y + 1)
                region = texture.get_region(left, bottom, width, height)
                region.anchor_x = Global.HALF_BLOCK
                region.anchor_y = Global.HALF_BLOCK
                Data.cache[name+'_'+str(x)+'x'+str(y)] = region

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
    def get_image(fdir, cache):
        img = pyglet.resource.image(Data.direct(fdir + '.png', path=''))
        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2
        if cache:
            Data.cache[fdir] = img
        return img

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
