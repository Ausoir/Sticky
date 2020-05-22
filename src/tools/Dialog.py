from src.tools.Data import Data


class Dialog:
    data = None

    @staticmethod
    def init():
        Dialog.data = Dialog.to_dict(Data.process_raw(Data.read('data/raw/dialog.txt')))

    @staticmethod
    def get(topic, var=None):
        index = 0
        if topic in Dialog.data:
            data = Dialog.data[topic]
            if not var:
                return data
            r = ''
            for c in data:
                if c == '#':
                    r += str(var[index])
                    index += 1
                else:
                    r += c
            return r
        return topic

    @staticmethod
    def strlist(arg):
        return '[' + ','.join(arg) + ']'

    @staticmethod
    def nonstrlist(arg):
        return '[' + ','.join(str(x) for x in arg) + ']'

    @staticmethod
    def deepnonstrlist(arg, lvl):
        if lvl <= 1:
            return Dialog.nonstrlist(arg)
        return '[' + ','.join(Dialog.deepnonstrlist(x, lvl-1) for x in arg) + ']'

    @staticmethod
    def dict(arg):
        if not arg:
            return '[]'
        var = []
        for k, v in arg.items():
            var.append(k + ':' + str(v))
        return '[' + ','.join(var) + ']'

    @staticmethod
    def to_dict(arg, delimiter=','):
        r = {}
        if delimiter == ',':
            for i in arg:
                r[i[0]] = i[1]
        else:
            for i in arg:
                args = i.split(delimiter)
                r[args[0]] = args[1]
        return r

    @staticmethod
    def space(arg):
        return '[' + str(arg.x) + ',' + str(arg.y) + ']'

    @staticmethod
    def date(time):
        hour = time % 24
        day = str(int(time / 24))
        hour_m = time % 12
        if hour_m == 0:
            hour_m = '12'
        else:
            hour_m = str(hour_m)
        meridian = 'am'
        if hour >= 12:
            meridian = 'pm'
        return Dialog.get('Day') + ' ' + day + ' / ' + hour_m + ' ' + meridian

    @staticmethod
    def hours(time):
        if time == 0:
            return Dialog.get('Now')
        elif time == 1:
            return '1 ' + Dialog.get('hour')
        else:
            r = ''
            days = int(time / 24)
            if days > 0:
                if days == 1:
                    r = str(days) + ' ' + Dialog.get('day')
                else:
                    r = str(days) + ' ' + Dialog.get('days')
            hours = time % 24
            if hours > 0:
                if days > 0:
                    r += ' ' + Dialog.get('and') + ' '
                r += str(hours) + ' ' + Dialog.get('hours')
            return r

    @staticmethod
    def numeral(number):
        if number == 0:
            return Dialog.get('zero')
        elif number == 1:
            return Dialog.get('one')
        elif number == 2:
            return Dialog.get('two')
        elif number == 3:
            return Dialog.get('three')
        elif number == 4:
            return Dialog.get('four')
        elif number == 5:
            return Dialog.get('five')
        elif number == 6:
            return Dialog.get('six')
        elif number == 7:
            return Dialog.get('seven')
        elif number == 8:
            return Dialog.get('eight')
        elif number == 9:
            return Dialog.get('nine')
        else:
            return str(number)

    @staticmethod
    def describe_terrain(tile):
        r = tile.name.title()
        speed = tile.get_speed()
        if tile.speed <= -10:
            r += '\n' + Dialog.get('terrain wall')
        elif speed != 0:
            r += '\n' + Dialog.get('terrain speed', [str(speed)])
        if tile.light > 0:
            r += '\n' + Dialog.get('terrain lit')
        if tile.roof > 0:
            r += '\n' + Dialog.get('terrain roof')
        return r

    @staticmethod
    def sign(measure):
        if measure >= 0:
            return '+' + str(measure)
        else:
            return str(measure)

    @staticmethod
    def weight(measure):
        return str(measure) + Dialog.get('kg')

    @staticmethod
    def armor(measure):
        return Dialog.get('Armor') + ': ' + str(measure)

    @staticmethod
    def durability(hp, max_hp):
        if hp:
            if max_hp:
                return Dialog.get('Durability') + ': ' + str(hp) + '/' + str(max_hp)
            else:
                return Dialog.get('Durability') + ': ' + str(hp) + ' (' + Dialog.get('!repair') + ')'
        else:
            return Dialog.get('!durability')
