from enum import Enum


QUANTIFIER_TYPES = Enum('quantifier_types', 'GREEDY LAZY')


class Node(object):

    def __init__(self, next_node=None):
        self.next_node = next_node

    def match(self, text, index, groups):
        raise NotImplementedError()

    def reset_repetition_count(self):
        self.next_node.reset_repetition_count()


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

    def match(self, text, index, groups):
        return (
            index < len(text) and
            self.start <= text[index] <= self.end and
            self.next_node.match(text, index + 1, groups)
        )


class OrStart(Node):

    def __init__(self, available_paths, inverse_match=False):
        self.available_paths = available_paths
        self.inverse_match = inverse_match
        self.inverse_match_allowed = True
        super(OrStart, self).__init__()

    def get_or_end(self):
        or_end = OrEnd(self)
        for available_path in self.available_paths:
            available_path.end.next_node = or_end
        self.next_node = or_end
        return or_end

    def match(self, text, index, groups):
        for available_path in self.available_paths:
            if (
                available_path.start.match(text, index, groups) and
                not self.inverse_match
            ):
                return True
        if (
            self.inverse_match and
            self.inverse_match_allowed and
            index < len(text)
        ):
            return self.next_node.next_node.match(text, index + 1, groups)
        else:
            return False

    def reset_repetition_count(self):
        for available_path in self.available_paths:
            available_path.start.reset_repetition_count()


class OrEnd(Node):

    def __init__(self, or_start_node):
        self.or_start_node = or_start_node

    def match(self, text, index, groups):
        if self.or_start_node.inverse_match:
            self.or_start_node.inverse_match_allowed = False
            return False
        else:
            return self.next_node.match(text, index, groups)


class GroupStart(Node):

    def __init__(self, group_number):
        self.group_number = group_number
        super(GroupStart, self).__init__()

    def match(self, text, index, groups):
        previous_group_start_index = groups[self.group_number].start
        groups[self.group_number] = \
            groups[self.group_number]._replace(start=index)
        self.reset_repetition_count()
        if self.next_node.match(text, index, groups):
            return True
        else:
            groups[self.group_number] = groups[self.group_number] \
                ._replace(start=previous_group_start_index)
            return False


class GroupEnd(Node):

    def __init__(self, group_number):
        self.group_number = group_number
        super(GroupEnd, self).__init__()

    def match(self, text, index, groups):
        previous_group_end_index = groups[self.group_number].end
        groups[self.group_number] = \
            groups[self.group_number]._replace(end=index)
        if self.next_node.match(text, index, groups):
            return True
        else:
            groups[self.group_number] = groups[self.group_number] \
                ._replace(end=previous_group_end_index)
            return False

    def reset_repetition_count(self):
        return


class Repeat(Node):

    def __init__(
        self,
        minimum_repetition,
        maximum_repetition,
        repeat_path_start,
        repeat_path_end,
        quantifier_type=QUANTIFIER_TYPES.GREEDY,
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
            else:
                self.number_of_repetitions_done -= 1
                return False
        else:
            if self.quantifier_type == QUANTIFIER_TYPES.GREEDY:
                return self.greedy_match(text, index, groups)
            else:
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
            else:
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
            else:
                self.number_of_repetitions_done -= 1
        return False

    def reset_repetition_count(self):
        self.number_of_repetitions_done = 0
        self.next_node.reset_repetition_count()


class EndAnchor(Node):

    def match(self, text, index, groups):
        return (
            index == len(text) and
            self.next_node.match(text, index, groups)
        )


class Destination(Node):

    def match(self, text, index, groups):
        return True
