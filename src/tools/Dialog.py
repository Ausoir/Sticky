from src.tools.Data import Data


class Dialog:
    dialog = Data.process_raw(Data.read('raw/dialog.txt'))

    @staticmethod
    def get(topic, var=None):
        index = 0
        for i in Dialog.dialog:
            if i[0] == topic:
                if not var:
                    return i[1]
                r = ''
                for c in i[1]:
                    if c == '#':
                        r += str(var[index])
                        index += 1
                    else:
                        r += c
                return r
        return topic.title()

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
        day = str(int(hour))
        hour_m = time % 12 + 1
        meridian = 'am'
        if hour + 1 >= 12:
            meridian = 'pm'
        return Dialog.get('time', [day, hour_m, meridian])

    @staticmethod
    def day(date):
        if date == 0:
            r = Dialog.get('anytime')
        elif date == 1:
            r = Dialog.get('half day')
        elif date == 2:
            r = Dialog.get('one day')
        else:
            word = Dialog.numeral(int(date / 2))
            if date % 2 == 1:
                r = Dialog.get('and half days', [word])
            else:
                r = Dialog.get('days', [word])
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
    def weight(measure):
        return str(measure) + Dialog.get('weigh')
