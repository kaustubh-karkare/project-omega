import regex_nodes

from tokenize import TOKENS
from collections import namedtuple


class RegexParserError(Exception):
    """Base class for exceptions in regexparser"""
    pass


Path = namedtuple('path', ['start', 'end'])


class RegexParser(object):

    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.total_groups = 0

    def parse_regex(self):
        source_node = regex_nodes.Source()
        previous_node = source_node
        while self.index < len(self.tokens):
            current_path_start, current_path_end = self.parse_token()
            previous_node.next_node = current_path_start
            previous_node = current_path_end
        previous_node.next_node = regex_nodes.Destination()
        return source_node, self.total_groups

    def check(self, token_type):
        return (
            self.index < len(self.tokens) and
            self.tokens[self.index].type == token_type
        )

    def ensure(self, token_type):
        assert self.check(token_type)
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
        if self.tokens[self.index].type in [
            TOKENS.ASTERISK,
            TOKENS.PLUS,
            TOKENS.QUESTION_MARK,
        ]:
            raise RegexParserError('No quantifiable token present')
        elif self.check(TOKENS.CARET):
            current_path_start = self.parse_start_anchor()
        elif self.check(TOKENS.DOLLAR):
            current_path_start = self.parse_end_anchor()
        elif self.check(TOKENS.ESCAPE_SEQUENCE):
            current_path_start, current_path_end = \
                self.parse_escape_sequence()
        elif self.check(TOKENS.OPENING_PARENTHESIS):
            current_path_start, current_path_end = self.parse_group()
        elif self.check(TOKENS.OPENING_BRACKET):
            current_path_start, current_path_end = \
                self.parse_character_class()
        elif self.check(TOKENS.DOT):
            current_path_start, current_path_end = self.parse_wildcard()
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

    def parse_start_anchor(self):
        self.ensure(TOKENS.CARET)
        return regex_nodes.StartAnchor()

    def parse_end_anchor(self):
        self.ensure(TOKENS.DOLLAR)
        return regex_nodes.EndAnchor()

    def parse_escape_sequence(self):
        self.ensure(TOKENS.ESCAPE_SEQUENCE)
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
            character_range = regex_nodes.CharacterRange(
                escape_sequence_range['start'],
                escape_sequence_range['end'],
            )
            character_ranges.append(
                Path(start=character_range, end=character_range)
            )
        or_start = regex_nodes.OrStart(character_ranges, inverse_match)
        or_end = or_start.get_or_end()
        return or_start, or_end

    def parse_literal(self):
        literal = self.next().value
        return regex_nodes.CharacterRange(literal, literal)

    def parse_group(self):
        self.ensure(TOKENS.OPENING_PARENTHESIS)
        self.total_groups += 1
        group_number = self.total_groups
        group_start = regex_nodes.GroupStart(group_number)
        previous_node = group_start
        while not self.check(TOKENS.CLOSING_PARENTHESIS):
            current_path_start, current_path_end = self.parse_token()
            previous_node.next_node = current_path_start
            previous_node = current_path_end
        self.ensure(TOKENS.CLOSING_PARENTHESIS)
        group_end = regex_nodes.GroupEnd(group_number)
        previous_node.next_node = group_end
        return group_start, group_end

    def parse_character_class(self):
        self.ensure(TOKENS.OPENING_BRACKET)
        inverse_match = False
        if self.check(TOKENS.CARET):
            self.ensure(TOKENS.CARET)
            inverse_match = True
        character_class_elements = []
        while not self.check(TOKENS.CLOSING_BRACKET):
            current_index = self.index
            lower_limit = self.next()
            upper_limit = None
            if self.check(TOKENS.MINUS) and self.index < len(self.tokens):
                self.ensure(TOKENS.MINUS)
                upper_limit = self.next()
            if upper_limit is not None:
                if (
                    lower_limit.type == TOKENS.ESCAPE_SEQUENCE or
                    upper_limit.type == TOKENS.ESCAPE_SEQUENCE or
                    lower_limit.value > upper_limit.value
                ):
                    raise RegexParserError('Invalid range in character class')
                character_range = regex_nodes.CharacterRange(
                    start=lower_limit.value,
                    end=upper_limit.value,
                )
                current_path_start, current_path_end = \
                    character_range, character_range
                character_class_elements.append(
                    Path(start=current_path_start, end=current_path_end)
                )
            else:
                self.index = current_index
                if self.check(TOKENS.ESCAPE_SEQUENCE):
                    current_path_start, current_path_end = \
                        self.parse_escape_sequence()
                    character_class_elements.append(
                        Path(start=current_path_start, end=current_path_end)
                    )
                else:
                    current_path_start = self.parse_literal()
                    current_path_end = current_path_start
                    character_class_elements.append(
                        Path(start=current_path_start, end=current_path_end)
                    )
        self.ensure(TOKENS.CLOSING_BRACKET)
        or_start = \
            regex_nodes.OrStart(character_class_elements, inverse_match)
        or_end = or_start.get_or_end()
        return or_start, or_end

    def parse_wildcard(self):
        self.ensure(TOKENS.DOT)
        wildcard_characters = []
        character_range = regex_nodes.CharacterRange(start='\n', end='\n')
        wildcard_characters.append(
            Path(start=character_range, end=character_range)
        )
        character_range = regex_nodes.CharacterRange(start='\r', end='\r')
        wildcard_characters.append(
            Path(start=character_range, end=character_range)
        )
        or_start = \
            regex_nodes.OrStart(wildcard_characters, inverse_match=True)
        or_end = or_start.get_or_end()
        return or_start, or_end

    def parse_brace_quantifier(self):
        minimum_repetition = None
        maximum_repetition = None
        start_index = self.index
        self.ensure(TOKENS.OPENING_BRACE)
        lower_limit = ''
        upper_limit = ''
        while self.check(TOKENS.DIGIT):
            lower_limit += self.next().value
        upper_limit_available = False
        if self.check(TOKENS.COMMA):
            self.ensure(TOKENS.COMMA)
            upper_limit_available = True
        else:
            upper_limit = lower_limit
        if upper_limit_available:
            while self.check(TOKENS.DIGIT):
                upper_limit += self.next().value
        if self.check(TOKENS.CLOSING_BRACE):
            self.ensure(TOKENS.CLOSING_BRACE)
        else:
            self.index = start_index
            return minimum_repetition, maximum_repetition
        if lower_limit == '':
            self.index = start_index
            return minimum_repetition, maximum_repetition
        minimum_repetition = int(lower_limit)
        if upper_limit == '':
            maximum_repetition = -1
        else:
            maximum_repetition = int(upper_limit)
        return minimum_repetition, maximum_repetition

    def parse_repetition_quantifier(
        self,
        current_path_start,
        current_path_end,
    ):
        minimum_repetition = None
        maximum_repetition = None
        if self.check(TOKENS.ASTERISK):
            self.ensure(TOKENS.ASTERISK)
            minimum_repetition = 0
            maximum_repetition = -1
        elif self.check(TOKENS.PLUS):
            self.ensure(TOKENS.PLUS)
            minimum_repetition = 1
            maximum_repetition = -1
        elif self.check(TOKENS.QUESTION_MARK):
            self.ensure(TOKENS.QUESTION_MARK)
            minimum_repetition = 0
            maximum_repetition = 1
        elif self.check(TOKENS.OPENING_BRACE):
            minimum_repetition, maximum_repetition = \
                 self.parse_brace_quantifier()
        if minimum_repetition is not None and maximum_repetition is not None:
            quantifier_node = None
            quantifier_type = regex_nodes.QUANTIFIER_TYPES.GREEDY
            if self.check(TOKENS.QUESTION_MARK):
                self.ensure(TOKENS.QUESTION_MARK)
                quantifier_type = regex_nodes.QUANTIFIER_TYPES.LAZY
            quantifier_node = regex_nodes.Repeat(
                minimum_repetition=minimum_repetition,
                maximum_repetition=maximum_repetition,
                repeat_path_start=current_path_start,
                repeat_path_end=current_path_end,
                quantifier_type=quantifier_type,
            )
            current_path_start = quantifier_node
            current_path_end = quantifier_node
        return current_path_start, current_path_end
