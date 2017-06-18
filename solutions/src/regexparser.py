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
        root_node = regexnodes.Root()
        previous_node = root_node
        while self.index < len(self.tokens):
            current_path_start, current_path_end = self.parse_token()
            previous_node.next_node = current_path_start
            previous_node = current_path_end
            self.index += 1
        previous_node.next_node = regexnodes.Leaf()
        return root_node

    def parse_token(self):
        current_path_start = None
        current_path_end = None
        if self.tokens[self.index][0] in [
            TOKENS.asterisk.name,
            TOKENS.plus.name,
            TOKENS.question_mark.name,
        ]:
            raise RegexParserError('No quantifiable token present')
        elif self.tokens[self.index][0] == TOKENS.caret.name:
            current_path_start = self.caret()
        elif self.tokens[self.index][0] == TOKENS.dollar.name:
            current_path_start = self.dollar()
        elif self.tokens[self.index][0] == TOKENS.escape_sequence.name:
            current_path_start = self.escape_sequence()
        elif self.tokens[self.index][0] in [
            TOKENS.literal.name,
            TOKENS.minus.name,
            TOKENS.digit.name,
        ]:
            current_path_start = self.literal()
        elif self.tokens[self.index][0] == TOKENS.opening_parenthesis.name:
            current_path_start, current_path_end = self.group()
        elif self.tokens[self.index][0] == TOKENS.opening_bracket.name:
            current_path_start = self.character_class()
        elif self.tokens[self.index][0] == TOKENS.dot.name:
            current_path_start = self.dot()
        if current_path_end is None:
            current_path_end = current_path_start
        current_path_start, current_path_end = (
            self.parse_repetition_quantifier(
                current_path_start,
                current_path_end
            )
        )
        return current_path_start, current_path_end

    def caret(self):
        return regexnodes.StartAnchor()

    def dollar(self):
        return regexnodes.EndAnchor()

    def parse_escape_sequence(self, escape_sequence):
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
        return escape_sequence_ranges, inverse_match

    def escape_sequence(self):
        self.index += 1
        if self.index >= len(self.tokens):
            raise RegexParserError('Trailing backslash not allowed')
        escape_sequence_ranges, inverse_match = \
            self.parse_escape_sequence(self.tokens[self.index][1])
        return regexnodes \
            .EscapeSequence(escape_sequence_ranges, inverse_match)

    def literal(self):
        return regexnodes.Literal(self.tokens[self.index][1])

    def group(self):
        self.index += 1
        group_start_instance = regexnodes.GroupStart()
        previous_node_instance = group_start_instance
        while (
            self.index < len(self.tokens) and
            self.tokens[self.index][0] != TOKENS.closing_parenthesis.name
        ):
            current_path_start, current_path_end = self.parse_token()
            previous_node_instance.next_node = current_path_start
            previous_node_instance = current_path_end
            self.index += 1
        if self.index == len(self.tokens):
            raise RegexParserError('Group missing closing parenthesis')
        group_end_instance = regexnodes.GroupEnd()
        previous_node_instance.next_node = group_end_instance
        return group_start_instance, group_end_instance

    def character_class(self):
        self.index += 1
        character_class_tokens = []
        while (
            self.index < len(self.tokens) and
            self.tokens[self.index][0] != TOKENS.closing_bracket.name
        ):
            character_class_tokens.append(self.tokens[self.index])
            self.index += 1
        if self.index == len(self.tokens):
            raise RegexParserError('Character class missing closing bracket')
        inverse_match = False
        if (
            len(character_class_tokens) > 0 and
            character_class_tokens[0][0] == TOKENS.caret.name
        ):
            inverse_match = True
            del character_class_tokens[0]
        character_class_items = []
        ii = 0
        while ii < len(character_class_tokens):
            if (
                ii + 2 < len(character_class_tokens) and
                character_class_tokens[ii + 1][0] == TOKENS.minus.name
            ):
                left_token = character_class_tokens[ii]
                right_token = character_class_tokens[ii + 2]
                if (
                    left_token[0] == TOKENS.escape_sequence.name or
                    right_token[0] == TOKENS.escape_sequence.name
                ):
                    raise RegexParserError('Trailing backslash not allowed')
                lower_limit = left_token[1]
                upper_limit = right_token[1]
                if lower_limit > upper_limit:
                    raise RegexParserError('Invalid range in character class')
                character_class_items.append(
                    regexnodes.CharacterRange(
                        lower_limit,
                        upper_limit
                    )
                )
                ii += 3
            else:
                if character_class_tokens[ii][0] == TOKENS \
                        .escape_sequence.name:
                    ii += 1
                    if ii >= len(character_class_tokens):
                        raise RegexParserError(
                            'Trailing backslash not allowed'
                        )
                    escape_sequence_ranges, escape_sequence_inverse_match = \
                        self.parse_escape_sequence(
                            character_class_tokens[ii][1]
                        )
                    character_class_items.append(
                        regexnodes.EscapeSequence(
                            escape_sequence_ranges,
                            escape_sequence_inverse_match
                        )
                    )
                else:
                    character_class_items.append(
                        regexnodes.Literal(
                            character_class_tokens[ii][1],
                        )
                    )
                ii += 1
        return regexnodes.CharacterClass(
            character_class_items,
            inverse_match
        )

    def dot(self):
        return regexnodes.Dot()

    def asterisk_quantifier(self, current_path_start, current_path_end):
        quantifier_node = None
        repetition_type = regexnodes.REPETITION_TYPES.greedy.name
        if (
            self.index + 1 < len(self.tokens) and
            self.tokens[self.index + 1][0] == TOKENS.question_mark.name
        ):
            self.index += 1
            repetition_type = regexnodes.REPETITION_TYPES.lazy.name
        quantifier_node = regexnodes.AsteriskQuantifier(
            repeat_path_start=current_path_start,
            repeat_path_end=current_path_end,
            repetition_type=repetition_type,
        )
        current_path_start = quantifier_node
        current_path_end = quantifier_node
        return current_path_start, current_path_end

    def plus_quantifier(self, current_path_start, current_path_end):
        current_path_end, _ = self.asterisk_quantifier(
            current_path_start,
            current_path_end
        )
        return current_path_start, current_path_end

    def question_mark_quantifier(self, current_path_start, current_path_end):
        quantifier_node = None
        repetition_type = regexnodes.REPETITION_TYPES.greedy.name
        if (
            self.index + 1 < len(self.tokens) and
            self.tokens[self.index + 1][0] == TOKENS.question_mark.name
        ):
            self.index += 1
            repetition_type = regexnodes.REPETITION_TYPES.lazy.name
        quantifier_node = regexnodes.QuestionMarkQuantifier(
            repeat_path_start=current_path_start,
            repeat_path_end=current_path_end,
            repetition_type=repetition_type,
        )
        current_path_start = quantifier_node
        current_path_end = current_path_end.next_node
        return current_path_start, current_path_end

    def parse_brace_quantifier(self):
        minimum_repetition = -1
        maximum_repetition = -1
        ii = self.index + 1 + 1
        brace_quantifier_token = ''
        while (
            ii < len(self.tokens) and
            self.tokens[ii][0] != TOKENS.closing_brace.name
        ):
            if (
                self.tokens[ii][0] == TOKENS.digit.name or
                self.tokens[ii][1] == ','
            ):
                brace_quantifier_token += self.tokens[ii][1]
            else:
                return minimum_repetition, maximum_repetition
            ii += 1
        lower_limit, separator, upper_limit = \
            brace_quantifier_token.partition(',')
        try:
            minimum_repetition = int(lower_limit)
        except ValueError:
            return minimum_repetition, maximum_repetition
        if separator == ',':
            if upper_limit == '':
                maximum_repetition = None
            else:
                try:
                    maximum_repetition = int(upper_limit)
                except ValueError:
                    minimum_repetition = -1
                    return minimum_repetition, maximum_repetition
        else:
            maximum_repetition = minimum_repetition
        self.index = ii
        return minimum_repetition, maximum_repetition

    def brace_quantifier(
        self,
        current_path_start,
        current_path_end,
        minimum_repetition,
        maximum_repetition,
    ):
        quantifier_node = regexnodes.BraceQuantifier(
            minimum_repetition,
            maximum_repetition,
            repeat_path_start=current_path_start,
            repeat_path_end=current_path_end,
        )
        current_path_start = quantifier_node
        current_path_end = quantifier_node
        return current_path_start, current_path_end

    def parse_repetition_quantifier(
        self,
        current_path_start,
        current_path_end
    ):
        if self.index + 1 >= len(self.tokens):
            return current_path_start, current_path_end
        if self.tokens[self.index + 1][0] == TOKENS.asterisk.name:
            self.index += 1
            current_path_start, current_path_end = (
                self.asterisk_quantifier(
                    current_path_start,
                    current_path_end
                )
            )
        elif self.tokens[self.index + 1][0] == TOKENS.plus.name:
            self.index += 1
            current_path_start, current_path_end = (
                self.plus_quantifier(
                    current_path_start,
                    current_path_end
                )
            )
        elif self.tokens[self.index + 1][0] == TOKENS.question_mark.name:
            self.index += 1
            current_path_start, current_path_end = (
                self.question_mark_quantifier(
                    current_path_start,
                    current_path_end,
                )
            )
        elif self.tokens[self.index + 1][0] == TOKENS.opening_brace.name:
            minimum_repetition, maximum_repetition = \
                self.parse_brace_quantifier()
            if minimum_repetition == -1:
                return current_path_start, current_path_end
            current_path_start, current_path_end = \
                self.brace_quantifier(
                    current_path_start,
                    current_path_end,
                    minimum_repetition,
                    maximum_repetition
                )
        return current_path_start, current_path_end
