from tokenize import tokenizer


class InitialState:

    def __init__(self):

        self.state_type = 'initial-state'
        self.next_state = None

    def match(self, text, index):
        return self.next_state.match(text, index)


class StartAnchor:

    def __init__(self):
        self.state_type = 'start-anchor'
        self.next_state = None

    def match(self, text, index):
        return self.next_state.match(text, index) if index == 0 else False


class CharRange:

    def __init__(self, char_ranges, acceptable_characters=True):
        self.char_ranges = char_ranges
        self.acceptable_characters = acceptable_characters

    def check_if_character_in_range(self, character):
        character_found = False
        for char_range in self.char_ranges:
            if (
                character >= char_range['start'] and
                character <= char_range['end']
            ):
                character_found = True
                break
        if self.acceptable_characters:
            return True if character_found else False
        return False if character_found else True


class ConsumeCharacter:

    def __init__(
        self,
        char_range_items,
        minimum_characters_to_consume=1,
        maximum_characters_to_consume=1
    ):
        self.state_type = 'consume-character'
        self.char_range_items = char_range_items
        self.minimum_characters_to_consume = minimum_characters_to_consume
        self.maximum_characters_to_consume = maximum_characters_to_consume
        self.next_state = None

    def check_if_acceptable_character(self, character):
        for char_range_item in self.char_range_items:
            if char_range_item.check_if_character_in_range(character):
                return True
        return False

    def match(self, text, index):
        # The match tries to consume as many character as possible
        for ii in range(self.minimum_characters_to_consume):
            if index >= len(text):
                return False
            if self.check_if_acceptable_character(text[index]):
                index += 1
            else:
                return False
        current_index = index
        # Consume as many character possible
        for ii in range(
            self.minimum_characters_to_consume,
            self.maximum_characters_to_consume
        ):
            if current_index >= len(text):
                break
            if self.check_if_acceptable_character(text[current_index]):
                current_index += 1
            else:
                break
        while current_index >= index:
            if self.next_state.match(text, current_index):
                return True
            else:
                current_index -= 1
        return False


class EndAnchor:

    def __init__(self):
        self.state_type = 'end-anchor'
        self.next_state = None

    def match(self, text, index):
        return self.next_state.match(text, index) \
            if index == len(text) else False


class FinalState:

    def __init__(self):
        self.state_type = 'final-state'
        self.next_state = None

    def match(self, text, index):
        return True


def parse_escape_character(escape_character, acceptable_characters=True):
    if escape_character in ['D', 'S', 'W']:
        acceptable_characters = not acceptable_characters
        escape_character = escape_character.lower()
    char_ranges = ()
    if escape_character == 'd':
        char_ranges += ({'start': '0', 'end': '9'},)
    elif escape_character == 's':
        char_ranges += ({'start': ' ', 'end': ' '},)
    elif escape_character == 'w':
        char_ranges += (
            {'start': '0', 'end': '9'},
            {'start': 'A', 'end': 'Z'},
            {'start': 'a', 'end': 'z'},
            {'start': '_', 'end': '_'},
        )
    else:
        char_ranges += ({'start': escape_character, 'end': escape_character},)
    return char_ranges, acceptable_characters


def parse_character_class(character_set_elements):
    character_set_tokens = tokenizer(character_set_elements)
    char_ranges = ()
    character_set_tokens_length = len(character_set_tokens)
    acceptable_characters = True
    if character_set_tokens_length == 0:
        return char_ranges, acceptable_characters
    start_index = 0
    if character_set_tokens[start_index][0] == 'caret':
        start_index += 1
        acceptable_characters = False
    ii = start_index
    while ii < character_set_tokens_length:
        if (
            ii + 2 < character_set_tokens_length and
            character_set_tokens[ii + 1][0] == 'literal' and
            character_set_tokens[ii + 1][1] == '-'
        ):
            left_token = character_set_tokens[ii]
            right_token = character_set_tokens[ii + 2]
            if (
                left_token[0] == 'escape-character' or
                right_token[0] == 'escape-character' or
                right_token[1] < left_token[1]
            ):
                raise Exception('Invalid character range in character set')
            current_range = ({'start': left_token[1], 'end': right_token[1]},)
            char_ranges += (CharRange(current_range, acceptable_characters),)
            ii += 3
        else:
            if character_set_tokens[ii][0] == 'escape-character':
                current_character_range, current_acceptable_range = (
                    parse_escape_character(
                        character_set_tokens[ii][1],
                        acceptable_characters
                    )
                )
                char_ranges += (
                    CharRange(
                        current_character_range,
                        current_acceptable_range
                    ),
                )
            else:
                current_range = (
                    {
                        'start': character_set_tokens[ii][1],
                        'end': character_set_tokens[ii][1]
                    },
                )
                char_ranges += (
                    CharRange(
                        current_range,
                        acceptable_characters
                    ),
                )
            ii += 1
    return char_ranges


def compile(pattern):
    tokens = tokenizer(pattern)
    initial_state = InitialState()
    previous_state = initial_state
    ii = 0
    while ii < len(tokens):
        if tokens[ii][0] == 'consume-character':
            raise Exception('No quantifiable token available')
        elif tokens[ii][0] == 'caret':
            previous_state.next_state = StartAnchor()
        elif tokens[ii][0] == 'dollar':
            previous_state.next_state = EndAnchor()
        else:
            char_range_items = ()
            if tokens[ii][0] == 'escape-character':
                char_ranges, acceptable_characters = \
                    parse_escape_character(tokens[ii][1])
                char_range_items += (
                    CharRange(char_ranges, acceptable_characters),
                )
            elif tokens[ii][0] == 'character-class':
                char_range_items += (parse_character_class(tokens[ii][1]))
            elif tokens[ii][0] == 'dot':
                character_ranges = (
                    {'start': '\r', 'end': '\r'},
                    {'start': '\n', 'end': '\n'},
                )
                char_range_items += (CharRange(character_ranges, False),)
            else:
                character_range = (
                    {'start': tokens[ii][1], 'end': tokens[ii][1]},
                )
                char_range_items += (CharRange(character_range),)
            minimum_characters_to_consume = 1
            maximum_characters_to_consume = 1
            if (
                ii + 1 < len(tokens) and
                tokens[ii + 1][0] == 'consume-character'
            ):
                ii += 1
                minimum_characters_to_consume = tokens[ii][2]['minimum']
                maximum_characters_to_consume = tokens[ii][2]['maximum']
            previous_state.next_state = ConsumeCharacter(
                char_range_items,
                minimum_characters_to_consume,
                maximum_characters_to_consume
            )
        ii += 1
        previous_state = previous_state.next_state
    previous_state.next_state = FinalState()
    return initial_state


def check(pattern, text):
    initial_state = compile(pattern)
    if initial_state.match(text, 0):
        return True
    else:
        for ii in range(1, len(text)):
            if initial_state.match(text, ii):
                return True
    return False
