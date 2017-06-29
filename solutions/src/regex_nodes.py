from enum import Enum


QUANTIFIER_TYPES = Enum('quantifier_types', 'GREEDY LAZY')


class Node(object):

    def __init__(self, next_node=None):
        self.next_node = next_node

    def check_if_character_acceptable(self, character):
        raise NotImplementedError()

    def match(self, text, index, groups):
        raise NotImplementedError()

    def reset_repeatition_count(self):
        raise NotImplementedError()


class Source(Node):

    def match(self, text, index, groups):
        return self.next_node.match(text, index, groups)


class StartAnchor(Node):

    def match(self, text, index, groups):
        return index == 0 and self.next_node.match(text, index, groups)


class CharacterRange(Node):

    def __init__(self, start, end):
        self.start = start
        self.end = end
        super(CharacterRange, self).__init__()

    def check_if_character_acceptable(self, character):
        return self.start <= character <= self.end

    def match(self, text, index, groups):
        return (
            index < len(text) and
            self.check_if_character_acceptable(text[index]) and
            self.next_node.match(text, index + 1, groups)
        )

    def reset_repeatition_count(self):
        self.next_node.reset_repeatition_count()


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

    def match(self, text, index, groups):
        return (
            index < len(text) and
            self.check_if_character_acceptable(text[index]) and
            self.next_node.match(text, index + 1, groups)
        )

    def reset_repeatition_count(self):
        self.next_node.reset_repeatition_count()


class GroupStart(Node):

    def __init__(self, group_number):
        self.group_number = group_number
        super(GroupStart, self).__init__()

    def match(self, text, index, groups):
        previous_group_start_index = groups[self.group_number][0]
        groups[self.group_number][0] = index
        self.reset_repeatition_count()
        if self.next_node.match(text, index, groups):
            return True
        groups[self.group_number][0] = previous_group_start_index
        return False

    def reset_repeatition_count(self):
        self.next_node.reset_repeatition_count()


class GroupEnd(Node):

    def __init__(self, group_number):
        self.group_number = group_number
        super(GroupEnd, self).__init__()

    def match(self, text, index, groups):
        previous_group_end_index = groups[self.group_number][1]
        groups[self.group_number][1] = index
        if self.next_node.match(text, index, groups):
            return True
        groups[self.group_number][1] = previous_group_end_index
        return False

    def reset_repeatition_count(self):
        return


class Repeat(Node):

    def __init__(
        self,
        minimum_repetition,
        maximum_repetition,
        repeat_path_start,
        repeat_path_end,
        quantifier_type=QUANTIFIER_TYPES.GREEDY.name,
    ):
        self.minimum_repetition = minimum_repetition
        self.maximum_repetition = maximum_repetition
        self.number_of_repetitions_done = 0
        self.repeat_path_start = repeat_path_start
        repeat_path_end.next_node = self
        self.quantifier_type = quantifier_type
        super(Repeat, self).__init__()

    def match(self, text, index, groups):
        if self.number_of_repetitions_done < self.minimum_repetition:
            # If the node has been repeated less than the minimum repetition
            # specified by the quantifer then repeat the path enclosed by the
            # quantifier node
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index, groups):
                return True
            self.number_of_repetitions_done -= 1
            return False
        else:
            if self.quantifier_type == QUANTIFIER_TYPES.GREEDY.name:
                return self.greedy_match(text, index, groups)
            return self.lazy_match(text, index, groups)

    def greedy_match(self, text, index, groups):
        # The quantifier being greedy will consume as many character
        # as possible.
        if (
            self.maximum_repetition == -1 or
            self.number_of_repetitions_done < self.maximum_repetition
        ):
            # If their is no limit on repetition or the node has been
            # repeated less than the maximum repetition limit then
            # repeat the path enclosed by the quantifier.
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index, groups):
                return True
            self.number_of_repetitions_done -= 1
        # consume zero character and go to the next node.
        return self.next_node.match(text, index, groups)

    def lazy_match(self, text, index, groups):
        # The quantifier being lazy will consume as less character as possible

        # Consume zero character.
        if self.next_node.match(text, index, groups):
            return True
        if (
            self.maximum_repetition == -1 or
            self.number_of_repetitions_done < self.maximum_repetition
        ):
            # If their is no limit on repetition or the node has been
            # repeated less than the maximum repetition limit then
            # repeat the path enclosed by the quantifier.
            self.number_of_repetitions_done += 1
            if self.repeat_path_start.match(text, index, groups):
                return True
            self.number_of_repetitions_done -= 1
        return False

    def reset_repeatition_count(self):
        self.number_of_repetitions_done = 0
        self.next_node.reset_repeatition_count()


class EndAnchor(Node):

    def match(self, text, index, groups):
        return (
            index == len(text) and
            self.next_node.match(text, index, groups)
        )


class Destination(Node):

    def match(self, text, index, groups):
        return True
