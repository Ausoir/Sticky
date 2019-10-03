def parse(data):
    r = []
    raw = ''
    while data:
        code = data[0]
        data = data[1:]
        if code == '[':
            data, result = parse(data)
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


test = parse('[u,4,body_1x0,[1,0,0]],[d,4,body_2x0,[1,0,0]]')
print(test)
