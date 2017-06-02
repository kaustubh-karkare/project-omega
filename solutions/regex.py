import logging
import string
import sys

SPECIAL_CHARACTERS = ['d', 's', 'w', 'D', 'S', 'W']
MAXIMUM_REPETITIONS = 1000


def special_character_ascii_range(element):
    ascii_range_limits = []
    if element == 'd':
        ascii_range_limits.append([ord('0'), ord('9')])
    elif element == 's':
        ascii_range_limits.append([ord(' '), ord(' ')])
    elif element == 'w':
        ascii_range_limits.append([ord('0'), ord('9')])
        ascii_range_limits.append([ord('A'), ord('Z')])
        ascii_range_limits.append([ord('a'), ord('z')])
        ascii_range_limits.append([ord('_'), ord('_')])
    elif element == 'D':
        ascii_range_limits.append([0, ord('0') - 1])
        ascii_range_limits.append([ord('9') + 1, 127])
    elif element == 'S':
        ascii_range_limits.append([0, ord(' ') - 1])
        ascii_range_limits.append([ord(' ') + 1, 127])
    elif element == 'W':
        ascii_range_limits.append([0, ord(' ') - 1])
        ascii_range_limits.append([ord(' ') + 1, ord('0') - 1])
        ascii_range_limits.append([ord('9') + 1, ord('A') - 1])
        ascii_range_limits.append([ord('Z') + 1, ord('_') - 1])
        ascii_range_limits.append([ord('_') + 1, ord('a') - 1])
        ascii_range_limits.append([ord('z') + 1, 127])
    else:
        logging.error('Special character is invalid')
        sys.exit(1)
    valid_ascii_codes = list()
    for ascii_range in ascii_range_limits:
        while ascii_range[0] <= ascii_range[1]:
            valid_ascii_codes.append(ascii_range[0])
            ascii_range[0] += 1
    return valid_ascii_codes


def escape_character_ascii_range(pattern, index):
    valid_ascii_range = list()
    index += 1
    try:
        if pattern[index] in SPECIAL_CHARACTERS:
            valid_ascii_range = special_character_ascii_range(pattern[index])
        else:
            # Escape character will be treated as a literal
            valid_ascii_range.append(ord(pattern[index]))
    except IndexError:
        logging.error('Escape character is missing')
        raise
    index += 1
    return valid_ascii_range, index


def parse_character_class(elements, index):
    ascii_range = list()
    if index >= len(elements):
        return ascii_range, index
    if elements[index] == '\\':
        ascii_range, index = escape_character_ascii_range(elements, index)
    elif elements[index] == '-':
        if index == len(elements) - 1:
            ascii_range.append(ord('-'))
        elif elements[0] == '^' and index == 1:
            ascii_range.append(ord('-'))
        elif elements[0] == '-':
            ascii_range.append(ord('-'))
        else:
            logging.error('Character class has invalid -')
            sys.exit(1)
        index += 1
    else:
        ascii_range.append(ord(elements[index]))
        index += 1
    return ascii_range, index


def character_class(pattern, index):
    ii = index + 1
    elements = ''
    while ii < len(pattern) and pattern[ii] != ']':
        if pattern[ii] == '\\':
            elements += pattern[ii]
            ii += 1
            try:
                elements += pattern[ii]
            except IndexError:
                logging.error('Invalid escape character')
                raise
        else:
            elements += pattern[ii]
        ii += 1
    if ii >= len(pattern):
        logging.error('Character class missing closing bracket')
        sys.exit(1)
    index = ii + 1
    ii = 0
    acceptable_tokens = True
    if len(elements):
        if elements[ii] == '^':
            acceptable_tokens = False
            ii += 1
    ascii_range = list()
    while ii < len(elements):
        lower_ascii_codes, ii = parse_character_class(elements, ii)
        if ii < len(elements) and len(lower_ascii_codes) == 1 \
                and elements[ii] == '-':
            higher_ascii_codes, temporary_index = \
                parse_character_class(elements, ii + 1)
            if len(higher_ascii_codes) == 1:
                if lower_ascii_codes[0] <= higher_ascii_codes:
                    while lower_ascii_codes[0] <= \
                            higher_ascii_codes[0]:
                        ascii_range.append(lower_ascii_codes[0])
                        lower_ascii_codes[0] += 1
                    ii = temporary_index
                else:
                    logging.error('Range for character class not possible')
                    sys.exit(1)
            else:
                ascii_range += lower_ascii_codes
        else:
            ascii_range += lower_ascii_codes
    if acceptable_tokens:
        return ascii_range, index
    else:
        valid_ascii_range = list()
        for ii in range(128):
            if ii not in ascii_range:
                valid_ascii_range.append(ii)
        return valid_ascii_range, index


def get_number_of_repetitions(pattern, index):
    minimum_number_of_repetitions = -1
    maximum_number_of_repitions = -1
    literals_between_brackets = ''
    ii = index + 1
    treat_elements_as_literals = False

    while ii < len(pattern) and pattern[ii] != '}':
        if pattern[ii] not in \
                [',', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            treat_elements_as_literals = True
            break
        literals_between_brackets += pattern[ii]
        ii += 1

    if not treat_elements_as_literals and ii < len(pattern):
        lower_limit, _, upper_limit = literals_between_brackets.partition(',')
        if lower_limit != '':
            minimum_number_of_repetitions = string.atoi(lower_limit)
        if upper_limit != '':
            maximum_number_of_repitions = string.atoi(upper_limit)
        else:
            maximum_number_of_repitions = minimum_number_of_repetitions
        if minimum_number_of_repetitions > -1:
            index = ii + 1
    return minimum_number_of_repetitions, maximum_number_of_repitions, index


class State:

    def __init__(self, pattern, index):

        self.next_state = None
        self.minimum_repetitions = 1
        self.maximum_repetitions = 1
        self.valid_paths = list()
        if index >= len(pattern):
            return
        # Evaluate valid paths for next state
        if pattern[index] == '\\':
            self.valid_paths, index = \
                escape_character_ascii_range(pattern, index)
        elif pattern[index] in ['+', '?', '*']:
            logging.error('Quantifiable token is missing')
            sys.exit(1)
        elif pattern[index] == '[':
            self.valid_paths, index = character_class(pattern, index)
        elif pattern[index] == '.':
            for ii in range(ord('\n')):
                self.valid_paths.append(ii)
            for ii in range(ord('\n') + 1, ord('\r')):
                self.valid_paths.append(ii)
            for ii in range(ord('\r') + 1, 128):
                self.valid_paths.append(ii)
            index += 1
        else:
            self.valid_paths.append(ord(pattern[index]))
            index += 1

        if index < len(pattern):
            # Check for repetition_qualifier
            if pattern[index] == '?':
                self.minimum_repetitions = 0
                self.maximum_repetitions = 1
                index += 1
            elif pattern[index] == '*':
                self.minimum_repetitions = 0
                self.maximum_repetitions = MAXIMUM_REPETITIONS
                index += 1
            elif pattern[index] == '+':
                self.minimum_repetitions = 1
                self.maximum_repetitions = MAXIMUM_REPETITIONS
                index += 1
            elif pattern[index] == '{':
                lower_limit, upper_limit, index = \
                    get_number_of_repetitions(pattern, index)
                if lower_limit > -1:
                    self.minimum_repetitions = lower_limit
                    self.maximum_repetitions = upper_limit
            else:
                pass

        self.next_state = State(pattern, index)


def match_text(current_state, text, index):
    if current_state.next_state is None and index >= len(text):
        return True

    if index >= len(text):
        if current_state.minimum_repetitions == 0:
            return match_text(current_state.next_state, text, index)
        else:
            return False
    lower_limit = current_state.minimum_repetitions
    upper_limit = current_state.maximum_repetitions
    for ii in range(lower_limit):
        if (
            index < len(text) and
            ord(text[index]) in current_state.valid_paths
        ):
            index += 1
        else:
            return False

    if match_text(current_state.next_state, text, index):
        return True

    for ii in range(int(lower_limit), int(upper_limit)):
        if (
            index < len(text) and
            ord(text[index]) in current_state.valid_paths
        ):
            index += 1
            if match_text(current_state.next_state, text, index):
                return True
        else:
            return match_text(current_state.next_state, text, index)
    return False


def check(pattern, text):
    match_start_from_beginning = False
    pattern = pattern.rstrip('$')
    if len(pattern) and pattern[0] == '^':
        match_start_from_beginning = True
        pattern = pattern.lstrip('^')
    initial_state = State(pattern, 0)
    if match_text(initial_state, text, 0):
        return True
    elif not match_start_from_beginning:
        for ii in range(1, len(text)):
            if match_text(initial_state, text, ii):
                return True
    return False
