from enum import Enum


QUANTIFIER_TYPES = Enum('quantifier_types', 'GREEDY LAZY')


class Node(object):

    def __init__(self, next_node=None):
        self.next_node = next_node

    def check_if_character_acceptable(self, character):
        raise NotImplementedError()

    def match(self, text, index):
        return (
            index < len(text) and
            self.check_if_character_acceptable(text[index]) and
            self.next_node.match(text, index + 1)
        )


class Source(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class StartAnchor(Node):

    def match(self, text, index):
        return index == 0 and self.next_node.match(text, index)


class Dot(Node):

    def check_if_character_acceptable(self, character):
        return character != '\n' and character != '\r'


class CharacterRange(Node):

    def __init__(self, start, end):
        self.start = start
        self.end = end
        super(CharacterRange, self).__init__()

    def check_if_character_acceptable(self, character):
        return self.start <= character <= self.end


class Or(Node):

    def __init__(self, character_ranges, inverse_match=False):
        self.character_ranges = character_ranges
        self.inverse_match = inverse_match
        super(Or, self).__init__()

    def check_if_character_acceptable(self, character):
        character_found = False
        for character_range in self.character_ranges:
            if character_range.check_if_character_acceptable(character):
                character_found = True
                break
        if not self.inverse_match:
            return character_found
        return not character_found


class GroupStart(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class GroupEnd(Node):

    def match(self, text, index):
        return self.next_node.match(text, index)


class Repeat(Node):

    def __init__(
        self,
        minimum_repetition,
        maximum_repetition_limit,
        repeat_path_start,
        repeat_path_end,
        quantifier_type=QUANTIFIER_TYPES.GREEDY.name,
    ):
        self.minimum_repetition = minimum_repetition
        self.maximum_repetition_limit = maximum_repetition_limit
        self.number_of_repetitions_done = 0
        self.repeat_path_start = repeat_path_start
        repeat_path_end.next_node = self
        self.quantifier_type = quantifier_type
        super(Repeat, self).__init__()

    def match(self, text, index):
        if self.number_of_repetitions_done < self.minimum_repetition:
            # If the node has been repeated less than the minimum repetition
            # specified by the quantifer then repeat the path enclosed by the
            # quantifier node
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index):
                return True
            self.number_of_repetitions_done -= 1
            return False
        else:
            if self.quantifier_type == QUANTIFIER_TYPES.GREEDY.name:
                return self.greedy_match(text, index)
            else:
                return self.lazy_match(text, index)

    def greedy_match(self, text, index):
        # The quantifier being greedy will consume as many character
        # as possible.
        if (
            self.maximum_repetition_limit is None or
            self.number_of_repetitions_done < self.maximum_repetition_limit
        ):
            # If their is no limit on repetition or the node has been
            # repeated less than the maximum repetition limit then
            # repeat the path enclosed by the quantifier.
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index):
                return True
            self.number_of_repetitions_done -= 1
        # consume zero character and go to the next node.
        return self.next_node.match(text, index)

    def lazy_match(self, text, index):
        # The quantifier being lazy will consume as less character as possible

        # Consume zero character.
        if self.next_node.match(text, index):
            return True
        if (
            self.maximum_repetition_limit is None or
            self.number_of_repetitions_done < self.maximum_repetition_limit
        ):
            # If their is no limit on repetition or the node has been
            # repeated less than the maximum repetition limit then
            # repeat the path enclosed by the quantifier.
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index):
                return True
            self.number_of_repetitions_done -= 1
        return False


class EndAnchor(Node):

    def match(self, text, index):
        return index == len(text) and self.next_node.match(text, index)


class Destination(Node):

    def match(self, text, index):
        return True
