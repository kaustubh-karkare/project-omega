import regexnodes

from tokenize import TOKENS


class RegexParserError(Exception):
    """Base class for exceptions in regexparser"""
    pass


class RegexParser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def parse_regex(self):
        source_node = regexnodes.Source()
        previous_node = source_node
        while self.index < len(self.tokens):
            current_path_start, current_path_end = self.parse_token()
            previous_node.next_node = current_path_start
            previous_node = current_path_end
        previous_node.next_node = regexnodes.Destination()
        return source_node

    def check(self, token_name):
        return (
            self.index < len(self.tokens) and
            self.tokens[self.index].name == token_name
        )

    def ensure(self, token_name):
        assert self.check(token_name)
        self.index += 1

    def next(self):
        if self.index >= len(self.tokens):
            raise RegexParserError('Looking for literal but EOL found')
        token = self.tokens[self.index]
        self.index += 1
        return token

    def parse_token(self):
        current_path_start = None
        current_path_end = None
        if self.tokens[self.index].name in [
            TOKENS.ASTERISK.name,
            TOKENS.PLUS.name,
            TOKENS.QUESTION_MARK.name,
        ]:
            raise RegexParserError('No quantifiable token present')
        elif self.check(TOKENS.CARET.name):
            current_path_start = self.parse_caret()
        elif self.check(TOKENS.DOLLAR.name):
            current_path_start = self.parse_dollar()
        elif self.check(TOKENS.ESCAPE_SEQUENCE.name):
            current_path_start = self.parse_escape_sequence()
        elif self.check(TOKENS.OPENING_PARENTHESIS.name):
            current_path_start, current_path_end = self.parse_group()
        elif self.check(TOKENS.OPENING_BRACKET.name):
            current_path_start = self.parse_character_class()
        elif self.check(TOKENS.DOT.name):
            current_path_start = self.parse_dot()
        else:
            current_path_start = self.parse_literal()
        if current_path_end is None:
            current_path_end = current_path_start
        current_path_start, current_path_end = (
            self.parse_repetition_quantifier(
                current_path_start,
                current_path_end,
            )
        )
        return current_path_start, current_path_end

    def parse_caret(self):
        self.ensure(TOKENS.CARET.name)
        return regexnodes.StartAnchor()

    def parse_dollar(self):
        self.ensure(TOKENS.DOLLAR.name)
        return regexnodes.EndAnchor()

    def parse_escape_sequence(self):
        self.ensure(TOKENS.ESCAPE_SEQUENCE.name)
        escape_sequence = self.next().value
        escape_sequence_ranges = []
        inverse_match = False
        if escape_sequence in ['D', 'S', 'W']:
            inverse_match = True
            escape_sequence = escape_sequence.lower()
        if escape_sequence == 'd':
            escape_sequence_ranges.append({'start': '0', 'end': '9'})
        elif escape_sequence == 's':
            escape_sequence_ranges.append({'start': ' ', 'end': ' '})
        elif escape_sequence == 'w':
            escape_sequence_ranges.append({'start': '0', 'end': '9'})
            escape_sequence_ranges.append({'start': 'A', 'end': 'Z'})
            escape_sequence_ranges.append({'start': 'a', 'end': 'z'})
            escape_sequence_ranges.append({'start': '_', 'end': '_'})
        else:
            escape_sequence_ranges.append(
                {'start': escape_sequence, 'end': escape_sequence}
            )
        character_ranges = []
        for escape_sequence_range in escape_sequence_ranges:
            character_ranges.append(
                regexnodes.CharacterRange(
                    escape_sequence_range['start'],
                    escape_sequence_range['end'],
                )
            )
        return regexnodes.Or(character_ranges, inverse_match)

    def parse_literal(self):
        literal = self.next().value
        return regexnodes.CharacterRange(literal, literal)

    def parse_group(self):
        self.ensure(TOKENS.OPENING_PARENTHESIS.name)
        group_start = regexnodes.GroupStart()
        previous_node = group_start
        while not self.check(TOKENS.CLOSING_PARENTHESIS.name):
            current_path_start, current_path_end = self.parse_token()
            previous_node.next_node = current_path_start
            previous_node = current_path_end
        try:
            self.ensure(TOKENS.CLOSING_PARENTHESIS.name)
        except AssertionError:
            raise RegexParserError('Group missing closing parenthesis')
        group_end = regexnodes.GroupEnd()
        previous_node.next_node = group_end
        return group_start, group_end

    def parse_character_class(self):
        self.ensure(TOKENS.OPENING_BRACKET.name)
        inverse_match = False
        try:
            self.ensure(TOKENS.CARET.name)
            inverse_match = True
        except AssertionError:
            pass
        character_class_elements = []
        while not self.check(TOKENS.CLOSING_BRACKET.name):
            if (
                self.index + 2 < len(self.tokens) and
                self.tokens[self.index + 1].name == TOKENS.MINUS.name and
                self.tokens[self.index + 2].name != \
                    TOKENS.CLOSING_BRACKET.name
            ):
                # If the current literal is part of an ascii range.
                if self.check(TOKENS.ESCAPE_SEQUENCE.name):
                    raise RegexParserError('Invalid range in character class')
                else:
                    start = self.next()
                self.ensure(TOKENS.MINUS.name)
                if self.check(TOKENS.ESCAPE_SEQUENCE.name):
                    raise RegexParserError('Invalid range in character class')
                else:
                    end = self.next()
                start = start.value
                end = end.value
                if start > end:
                    raise RegexParserError('Invalid range in character class')
                character_class_elements.append(
                    regexnodes.CharacterRange(
                        start,
                        end,
                    )
                )
            else:
                if self.check(TOKENS.ESCAPE_SEQUENCE.name):
                    character_class_elements \
                        .append(self.parse_escape_sequence())
                else:
                    character_class_elements.append(self.parse_literal())
        self.ensure(TOKENS.CLOSING_BRACKET.name)
        return regexnodes.Or(character_class_elements, inverse_match)

    def parse_dot(self):
        self.ensure(TOKENS.DOT.name)
        return regexnodes.Dot()

    def parse_brace_quantifier(self):
        minimum_repetition = -1
        maximum_repetition_limit = -1
        start_index = self.index
        self.ensure(TOKENS.OPENING_BRACE.name)
        lower_limit = ''
        upper_limit = ''
        while self.check(TOKENS.DIGIT.name):
            lower_limit += self.next().value
        upper_limit_available = False
        try:
            self.ensure(TOKENS.COMMA.name)
            upper_limit_available = True
        except AssertionError:
            upper_limit = lower_limit
        if upper_limit_available:
            while self.check(TOKENS.DIGIT.name):
                upper_limit += self.next().value
        try:
            self.ensure(TOKENS.CLOSING_BRACE.name)
        except AssertionError:
            self.index = start_index
            return minimum_repetition, maximum_repetition_limit
        if lower_limit == '':
            self.index = start_index
            return minimum_repetition, maximum_repetition_limit
        minimum_repetition = int(lower_limit)
        if upper_limit == '':
            maximum_repetition_limit = None
        else:
            maximum_repetition_limit = int(upper_limit)
        return minimum_repetition, maximum_repetition_limit

    def parse_repetition_quantifier(
        self,
        current_path_start,
        current_path_end,
    ):
        minimum_repetition = -1
        maximum_repetition_limit = -1
        if self.check(TOKENS.ASTERISK.name):
            self.ensure(TOKENS.ASTERISK.name)
            minimum_repetition = 0
            maximum_repetition_limit = None
        elif self.check(TOKENS.PLUS.name):
            self.ensure(TOKENS.PLUS.name)
            minimum_repetition = 1
            maximum_repetition_limit = None
        elif self.check(TOKENS.QUESTION_MARK.name):
            self.ensure(TOKENS.QUESTION_MARK.name)
            minimum_repetition = 0
            maximum_repetition_limit = 1
        elif self.check(TOKENS.OPENING_BRACE.name):
            minimum_repetition, maximum_repetition_limit = \
                 self.parse_brace_quantifier()
        if minimum_repetition != -1 and maximum_repetition_limit != -1:
            quantifier_node = None
            quantifier_type = regexnodes.QUANTIFIER_TYPES.GREEDY.name
            try:
                self.ensure(TOKENS.QUESTION_MARK.name)
                quantifier_type = regexnodes.QUANTIFIER_TYPES.LAZY.name
            except AssertionError:
                pass
            quantifier_node = regexnodes.Repeat(
                minimum_repetition=minimum_repetition,
                maximum_repetition_limit=maximum_repetition_limit,
                repeat_path_start=current_path_start,
                repeat_path_end=current_path_end,
                quantifier_type=quantifier_type,
            )
            current_path_start = quantifier_node
            current_path_end = quantifier_node
        return current_path_start, current_path_end
