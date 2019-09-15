class Dialog:
    @staticmethod
    def date(date):
        if date == 1:
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
