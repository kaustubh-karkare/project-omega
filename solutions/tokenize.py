import string

UPPER_LIMIT = 1000


def tokenizer(data):
    tokens = ()
    data_length = len(data)
    ii = 0
    while ii < data_length:
        if data[ii] == '\\':
            ii += 1
            if ii < data_length:
                tokens += (('escape-character', data[ii]),)
            else:
                raise Exception('Looking for literal but EOL found')

        elif data[ii] == '[':
            # Get character class elements
            first_index = ii + 1
            last_index = first_index
            while True:
                last_index = data.find(']', last_index)
                if last_index == -1:
                    raise Exception('Looking for literal but EOL found')
                if data[last_index - 1] == '\\':
                    last_index = last_index + 1
                else:
                    break
            tokens += (('character-class', data[first_index:last_index]),)
            ii = last_index

        elif data[ii] == '{':
            # Check if repitition range given or to treat as literal.
            first_index = ii + 1
            last_index = data.find('}', first_index)
            if last_index == -1:
                tokens += (('literal', data[ii]),)
                ii += 1
                continue
            lower_limit, separator, upper_limit = \
                data[first_index:last_index].partition(',')
            try:
                lower_limit = string.atoi(lower_limit)
            except ValueError:
                tokens += (('literal', data[ii]),)
                ii += 1
                continue
            if upper_limit == '' and separator == ',':
                upper_limit = UPPER_LIMIT
            elif upper_limit == '' and separator == '':
                upper_limit = lower_limit
            else:
                try:
                    upper_limit = string.atoi(upper_limit)
                except ValueError:
                    tokens += (('literal', data[ii]),)
                    ii += 1
                    continue
            if upper_limit < lower_limit:
                raise Exception('Invalid repitition limits')
            tokens += (
                (
                    'consume-character',
                    data[first_index - 1:last_index + 1],
                    {'minimum': lower_limit, 'maximum': upper_limit},
                ),
            )
            ii = last_index
        elif data[ii] == '?':
            tokens += (
                ('consume-character', '?', {'minimum': 0, 'maximum': 1}),
            )
        elif data[ii] == '*':
            tokens += (
                (
                    'consume-character',
                    '*',
                    {'minimum': 0, 'maximum': UPPER_LIMIT},
                ),
            )
        elif data[ii] == '+':
            tokens += (
                (
                    'consume-character',
                    '+',
                    {'minimum': 1, 'maximum': UPPER_LIMIT},
                ),
            )
        elif data[ii] == '.':
            tokens += (('dot', '.'),)
        elif data[ii] == '^':
            tokens += (('caret', '^'),)
        elif data[ii] == '$':
            tokens += (('dollar', '$'),)
        else:
            tokens += (('literal', data[ii]),)
        ii += 1
    return tokens
