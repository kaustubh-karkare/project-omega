from collections import namedtuple
from tokenize import tokenizer
from regexparser import RegexParser


Group = namedtuple('group', ['start', 'end'])


def check(pattern, text):
    pattern_tokens = tokenizer(pattern)
    source_node, total_groups = RegexParser(pattern_tokens).parse_regex()
    groups = [Group(start=None, end=None) for ii in range(total_groups + 1)]
    for ii in range(0, len(text) + 1):
        if source_node.match(text, ii, groups):
            return True
    return False
