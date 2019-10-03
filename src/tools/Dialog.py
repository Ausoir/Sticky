class Dialog:
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
        var = []
        for k, v in arg.items():
            var.append(k + ':' + str(v))
        return '[' + ','.join(var) + ']'

    @staticmethod
    def space(arg):
        return '[' + str(arg.x) + ',' + str(arg.y) + ']'

    @staticmethod
    def date(day):
        year = str(int(day / 360) + 1)
        month = int(day % 360 / 30) + 1
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        date = int(day % 30) + 1
        if date < 10:
            date = '0' + str(date)
        else:
            date = str(date)
        return '203' + year + '/' + month + '/' + date

    @staticmethod
    def day(date):
        if date == 0:
            r = 'anytime'
        elif date == 1:
            r = 'half a day'
        elif date == 2:
            r = 'one day'
        else:
            word = Dialog.numeral(int(date / 2))
            if date % 2 == 1:
                r = word + ' and a half days'
            else:
                r = word + ' days'
        return r

    @staticmethod
    def numeral(number):
        if number == 0:
            return 'zero'
        elif number == 1:
            return 'one'
        elif number == 2:
            return 'two'
        elif number == 3:
            return 'three'
        elif number == 4:
            return 'four'
        elif number == 5:
            return 'five'
        elif number == 6:
            return 'six'
        elif number == 7:
            return 'seven'
        elif number == 8:
            return 'eight'
        elif number == 9:
            return 'nine'
        else:
            return str(number)
