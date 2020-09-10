import os

import pyglet
from pyglet.image import Texture
from pyglet.image.atlas import TextureAtlas

from src.form.Animation import Animation
from src.form.Picture import Picture, Model


class Data:
    cache = {}
    graphics = {}
    registry_list = ['props', 'units', 'items', 'armors', 'weapons', 'headgears', 'miscellaneous', 'mercenaries']
    atlas = None

    @staticmethod
    def init():
        os.chdir('../')
        Data.atlas = TextureAtlas()
        Data.set_cache('none', Texture.create(1, 1))
        res = Data.process_raw(Data.read('data/raw/resource.txt'))
        for i in res:
            Data.initialize_image(i[0], i[1], i[2], i[3])
        for i in Data.get_files('data/unit', lambda f: f.endswith('.2d')):
            Data.set_cache(i, Data.get_cache_clip('data/unit/' + i))

    @staticmethod
    def initialize_animation():
        animation = Data.process_raw(Data.read('data/raw/animations.txt'))
        for i in animation:
            sequence = []
            for sprite in i[1]:
                image = Data.get_graphics(sprite)
                sequence.append(image)
            Data.set_cache(i[0], (sequence, i[2], i[3]))

    @staticmethod
    def direct(fdir, path=''):
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
    def get_graphics(fdir):
        if fdir[0] == '_':
            args = fdir.split('_')
            return Data.graphics[args[1]][int(args[3])][int(args[2])]
        return Data.get_cache(fdir)

    @staticmethod
    def set_cache(fdir, arg):
        if fdir not in Data.cache:
            Data.cache[fdir] = arg

    @staticmethod
    def get_track(fdir):
        directory = 'data/sound/' + fdir
        cache = Data.get_cache(directory)
        if not cache:
            cache = pyglet.media.StaticSource(pyglet.media.load(Data.direct(directory + '.wav')))
            Data.set_cache(directory, cache)
        return cache

    @staticmethod
    def get_image(fdir, cache):
        img = Data.atlas.add(pyglet.image.load(Data.direct('data/image/' + fdir + '.png')))
        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2
        if cache:
            Data.cache[fdir] = img
        return img

    @staticmethod
    def get_form(fdir, form=None, **kwargs):
        cache = Data.get_graphics(fdir)
        if not cache:
            cache = Data.get_image(fdir, True)
        if not form:
            if cache:
                if isinstance(cache, Texture):
                    return Picture(cache, **kwargs)
                elif isinstance(cache, tuple):
                    return Animation(cache[0], cache[1], cache[2])
                else:
                    return cache
        else:
            if form.startswith('Unit'):
                return Data.get_model(cache, int(form[4:]), 3, **kwargs)
            elif form == 'Head':
                return Data.get_model(cache, 1, 3, **kwargs)
            elif form == 'Humanoid':
                return Data.get_model(cache, 3, 3, **kwargs)
            elif form == 'Armor':
                width = int(cache.width / 3)
                height = int(cache.height / 3)
                r = Picture(cache.get_region(0, cache.height - height, width, height), **kwargs)
                r.reset()
                return r

    @staticmethod
    def get_model(image, cols, rows, **kwargs):  # ImageGrid would reverse rows
        seq = []
        width = int(image.width / cols)
        height = int(image.height / rows)
        for y in range(0, rows):
            for x in range(0, cols):
                left = width * x
                bottom = image.height - height * (y + 1)
                img = image.get_region(left, bottom, width, height)
                img.anchor_x = img.width / 2
                img.anchor_y = img.height / 2
                seq.append(img)
        return Model(seq, **kwargs)

    @staticmethod
    def initialize_image(name, texture, subset_size, anchor=None):
        Data.graphics[name] = []
        image = Data.atlas.add(pyglet.image.load(Data.direct('data/image/' + texture + '.png')))
        # image = pyglet.image.load(Data.direct('data/image/' + texture + '.png'))
        image_grid = pyglet.image.ImageGrid(image, subset_size[1], subset_size[0])
        seq = pyglet.image.TextureGrid(image_grid)
        i = 0
        for y in range(subset_size[1]):
            row = []
            for x in range(subset_size[0]):
                if anchor:
                    seq[i].anchor_x = anchor[0]
                    seq[i].anchor_y = anchor[1]
                else:
                    seq[i].anchor_x = int(seq[i].width / 2)
                    seq[i].anchor_y = int(seq[i].height / 2)
                row.append(seq[i])
                i += 1
            Data.graphics[name].insert(0, row)

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
                special = not special
            elif special:
                raw += code
            elif code == '|':
                raw += '\n'
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
    def get_line(fdir, name, row=False):
        cache = Data.get_cache(fdir)
        if cache:
            data = cache
        else:
            data = Data.process_raw(Data.read('data/raw/' + fdir))
            Data.set_cache(fdir, data)
        for k, i in enumerate(data):
            if i[0] == name:
                if row:
                    return k, i
                else:
                    return i
        if row:
            return None, None

    @staticmethod
    def get_cache_clip(fdir):
        r = []
        clip = Data.read(Data.direct(fdir))
        lines = clip.split('\n\n')
        r.append(Data.process_raw(lines[0]))
        r.append(Data.process_raw(lines[1]))
        r.append(Data.process_raw(lines[2]))
        return r

    @staticmethod
    def delete_all():
        for f in os.listdir('save/'):
            os.remove(Data.direct(f, 'save/'))

    @staticmethod
    def delete(directory):
        f_dir = Data.direct(directory)
        if Data.is_file(f_dir):
            os.remove(Data.direct(f_dir))
