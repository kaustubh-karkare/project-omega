from enum import Enum


REPETITION_TYPES = Enum('repetition_types', 'greedy lazy')


class Node(object):

    def __init__(self, next_node=None):
        self.next_node = next_node

    def check_if_character_acceptable(self, character):
        pass

    def match(self, text, index):
        return self.next_node.match(text, index + 1) if index < len(text) \
            and self.check_if_character_acceptable(text[index]) else False


class Source(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class StartAnchor(Node):

    def match(self, text, index):
        return self.next_node.match(text, index) if index == 0 else False


class Literal(Node):

    def __init__(self, literal):
        self.literal = literal
        super(Literal, self).__init__()

    def check_if_character_acceptable(self, character):
        return True if character == self.literal else False


class Dot(Node):

    def check_if_character_acceptable(self, character):
        return True if character != '\n' and character != '\r' else False


class Empty(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class EscapeSequence(Node):

    def __init__(self, escape_sequence_ranges, inverse_match=False):
        self.escape_sequence_ranges = escape_sequence_ranges
        self.inverse_match = inverse_match
        super(EscapeSequence, self).__init__()

    def check_if_character_acceptable(self, character):
        character_found = False
        for escape_sequence_range in self.escape_sequence_ranges:
            if (
                character >= escape_sequence_range['start'] and
                character <= escape_sequence_range['end']
            ):
                character_found = True
                break
        if not self.inverse_match:
            return True if character_found else False
        return True if not character_found else False


class CharacterRange(Node):

    def __init__(self, lower_limit, upper_limit):
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        super(CharacterRange, self).__init__()

    def check_if_character_acceptable(self, character):
        return True if character >= self.lower_limit and \
            character <= self.upper_limit else False


class CharacterClass(Node):

    def __init__(self, character_class_items, inverse_match=False):
        self.character_class_items = \
            character_class_items
        self.inverse_match = inverse_match
        super(CharacterClass, self).__init__()

    def check_if_character_acceptable(self, character):
        character_found = False
        for acceptable_item in self.character_class_items:
            if acceptable_item.check_if_character_acceptable(character):
                character_found = True
                break
        if not self.inverse_match:
            return True if character_found else False
        return True if not character_found else False


class GroupStart(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class GroupEnd(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class AsteriskQuantifier(Node):

    def __init__(
        self,
        repeat_path_start,
        repeat_path_end,
        repetition_type=REPETITION_TYPES.greedy.name,
    ):
        self.repeat_path_start = repeat_path_start
        repeat_path_end.next_node = self
        self.repetition_type = repetition_type
        super(AsteriskQuantifier, self).__init__()

    def match(self, text, index):
        if self.repetition_type == REPETITION_TYPES.lazy.name:
            return True if self.next_node.match(text, index) or \
                self.repeat_path_start.match(text, index) else False
        return True if self.repeat_path_start.match(text, index) or \
            self.next_node.match(text, index) else False


class QuestionMarkQuantifier(Node):

    def __init__(
        self,
        repeat_path_start,
        repeat_path_end,
        repetition_type=REPETITION_TYPES.greedy.name,
    ):
        self.repeat_path_start = repeat_path_start
        repeat_path_end.next_node = Empty()
        self.repetition_type = repetition_type
        super(QuestionMarkQuantifier, self) \
            .__init__(repeat_path_end.next_node)

    def match(self, text, index):
        if self.repetition_type == REPETITION_TYPES.lazy.name:
            return True if self.next_node.match(text, index) or \
                self.repeat_path_start.match(text, index) else False
        return True if self.repeat_path_start.match(text, index) or \
            self.next_node.match(text, index) else False


class BraceQuantifier(Node):

    def __init__(
        self,
        minimum_repetition,
        maximum_repetition,
        repeat_path_start,
        repeat_path_end,
    ):
        self.minimum_repetition = minimum_repetition
        self.maximum_repetition = maximum_repetition
        self.number_of_repetitions_done = 0
        self.repeat_path_start = repeat_path_start
        repeat_path_end.next_node = self
        super(BraceQuantifier, self).__init__()

    def match(self, text, index):
        if self.number_of_repetitions_done < self.minimum_repetition:
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index):
                return True
            self.number_of_repetitions_done -= 1
            return False
        else:
            if (
                self.maximum_repetition is None or
                self.number_of_repetitions_done < self.maximum_repetition
            ):
                self.number_of_repetitions_done += 1
                if self.repeat_path_start.match(text, index):
                    return True
                self.number_of_repetitions_done -= 1
            return self.next_node.match(text, index)


class EndAnchor(Node):

    def match(self, text, index):
        return self.next_node.match(text, index) \
            if index == len(text) else False


class Destination(Node):

    def match(self, text, index):
        return True
